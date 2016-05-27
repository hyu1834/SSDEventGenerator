import os
import sys
import re

# sudo blktrace -a read -a write -a discard -w 20 -d /dev/sda -o - | blkparse -i -
# sudo fstrim /

if len(sys.argv) < 2:
	print("Usage: python preprocessor.py <blktrace activity file>")
	exit()


activity_log = {}
command_durt = {"R": 0, "W": 0, "T": 0}
current_clock = {}
rwbs_count = {"R": 0, "W": 0, "T": 0}
activity = {}



# for every line in activity file
for line in open(sys.argv[1], 'r'):
	line = line.split()
	if len(line) < 8:
		continue

	try:
		event = line[0]
		cpu_id = int(line[1])
		seq_num = int(line[2])
		seconds = float(line[3])
		process_id = int(line[4])
		action_type = line[5]
		rwbs = line[6]
		description = ''.join(line[7:])
	except ValueError:
		continue

	if not any(action_type == accept_action for accept_action in ["D", "C"]):
		continue

	# ignore large difference time
	if not cpu_id in current_clock.keys():
		if (seconds - 0) > 1000:
			continue
		# set the current core second if it is the first one, and the difference > 1 second
		current_clock[cpu_id] = seconds
	else:
		if (seconds - current_clock[cpu_id]) > 1000:
			continue
		current_clock[cpu_id] = seconds

	
	if action_type == "D":
		match = re.match("(\d+\+\d).*$", description)
		if match and match.groups()[0]:
			activity_log[match.groups()[0]] = (seconds, rwbs)
	elif action_type == "C":
		try:
			match = re.match("(\d+\+\d).*$", description)
			if match and match.groups()[0] and activity_log[match.groups()[0]]:
				time_diff = seconds - activity_log[match.groups()[0]][0]
				# print(time_diff)
				if time_diff > 0:
					if "D" in rwbs:
						command_type = "T"
					elif "R" in rwbs:
						command_type = "R"
					elif "W" in rwbs:
						command_type = "W"

					command_durt[command_type] += time_diff
					rwbs_count[command_type] += 1

					activity[activity_log[match.groups()[0]][0]] = command_type

				del activity_log[match.groups()[0]]
		except KeyError:
			continue

# activity = {key:activity[key] for key in sorted(activity)}

statistic_fp = open("statistic.csv", 'w')
for key, value in command_durt.items():
	try:
		statistic_fp.write("%s  %s\n"%(key, value/rwbs_count[key]))
	except ZeroDivisionError:
		statistic_fp.write("%s  %s\n"%(key, 0))

activity_fp = open("activity.csv", "w")
for key in sorted(activity):
	activity_fp.write("%.10lf  %s\n"%(key, activity[key]))



