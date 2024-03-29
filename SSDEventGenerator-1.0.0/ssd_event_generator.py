import os
import sys
import random

import io_utils
import bash_utils
import trim_simulator_utils

def help(terminate = True):
	io_utils.usage("python ssd_event_generator -r <duration(second)>")
	io_utils.usage("python ssd_event_generator --real <duration(second)>")
	io_utils.usage("python ssd_event_generator -s <duration(second)> <real time> <write time> <trim time>")
	io_utils.usage("python ssd_event_generator --simulate <duration(second)> <real time> <write time> <trim time>", terminate = terminate)

class SSD_Event_Generator(object):
	def __init__(self, real_event_capture, simulate_event_capture, capture_duration, read_time, write_time, trim_time, concurrent_event):
		self.real_event_capture = real_event_capture
		self.simulate_event_capture = simulate_event_capture
		self.capture_duration = capture_duration
		self.read_time = read_time
		self.write_time = write_time
		self.trim_time = trim_time
		self.concurrent_event = concurrent_event


	def capture_real_event(self):
		# container for list of events
		cmd = "sudo blktrace -a read -a write -a discard -w %d -d /dev/sda -o - | blkparse -i -"%(self.capture_duration)
		execute, message = bash_utils.execute_bash_command(cmd, self.capture_duration + 5)
		if not execute:
			io_utils.stderr("Unable to capture real even, try simulate mode", terminate = True)	

		return message.split("\n")

	def capture_simulate_event(self):
		# 8,0    1       70     0.000039646   213  D  WS 415398104 + 176 [jbd2/sda5-8]
		# 8,0    1       71     0.000288625     0  C  WS 415398104 + 176 [0]
		CLOCK_SPEED = 0.000000010
		clock = 0.0
		events = {}
		
		# start generate
		while(clock < self.capture_duration):
			longest_event_time = 0
			generated_event = 0
			while(generated_event < concurrent_event):
				# generate a process, even through the generated event is no event
				generated_event += 1
				event_type = random.randint(0, 50) 
				# an event
				if event_type == 1:
					starting_block = random.randint(100000000, 999999999)
					next_n_block = random.randint(1, 1024)
					rwbs = random.random()
					# print(rwbs)
					# rwbs = random.randint(0, 2)
					command_issue_time = clock

					# read
					if 0 <= rwbs < 0.45:
						command_compt_time = clock + self.read_time
						events[command_issue_time] = ("D", "R", starting_block, next_n_block)
						events[command_compt_time] = ("C", "R", starting_block, next_n_block)
						if self.read_time > longest_event_time:
							longest_event_time = CLOCK_SPEED#self.read_time
					# write
					elif 0.45 <= rwbs < 0.55:
						command_compt_time = clock + self.write_time
						events[command_issue_time] = ("D", "W", starting_block, next_n_block)
						events[command_compt_time] = ("C", "W", starting_block, next_n_block)
						if self.write_time > longest_event_time:
							longest_event_time = CLOCK_SPEED#self.write_time
					# trim
					else:
						command_compt_time = clock + self.trim_time
						events[command_issue_time] = ("D", "D", starting_block, next_n_block)
						events[command_compt_time] = ("C", "D", starting_block, next_n_block)
						if self.trim_time > longest_event_time:
							longest_event_time = CLOCK_SPEED#self.trim_time
				else:
					longest_event_time += CLOCK_SPEED

			clock += longest_event_time

		return ["8,0    1       %s     %.9f   213  %s  %s %s + %s"%(seq_num, key, events[key][0], events[key][1], events[key][2], events[key][3]) for seq_num, key in enumerate(sorted(events.keys()))]

	def capture_event(self):
		if self.real_event_capture and capture_duration > 0:
			return trim_simulator_utils.trim_simulator_event_formatter(self.capture_real_event())
		elif self.simulate_event_capture and capture_duration > 0 and read_time > 0 and write_time > 0 and trim_time > 0:
			return trim_simulator_utils.trim_simulator_event_formatter(self.capture_simulate_event())
		else:
			help()



if __name__ == '__main__':
	argc = len(sys.argv)
	if argc < 3:
		help()

	real_event_capture = False
	simulate_event_capture = False
	capture_duration = -1
	read_time = -1
	write_time = -1
	trim_time = -1
	concurrent_event = 1

	# prase options
	index = 1
	while(index < argc):
		arg = sys.argv[index]
		if arg == "-r" or arg == "--real":
			real_event_capture = True
			try:
				capture_duration = int(sys.argv[index + 1])
				index += 1
			except IndexError:
				io_utils.stderr("Dangling -r or --real flag on command line", terminate = True)
		elif arg == "-s" or arg == "--simulate":	
			simulate_event_capture = True
			try:
				capture_duration = float(sys.argv[index + 1])
				read_time = float(sys.argv[index + 2])
				write_time = float(sys.argv[index + 3])
				trim_time = float(sys.argv[index + 4])
				index += 4
			except IndexError:
				io_utils.stderr("Dangling -s or --simulate flag on command line", terminate = True)
		elif arg == "-c" or arg == "--concurrent":
			try:
				concurrent_event = int(sys.argv[index + 1])
				index += 1
			except IndexError:
				io_utils.stderr("Dangling -c or --concurrent flag on command line", terminate = True)
		else:
			io_utils.stderr("Unrecognized option - %s"%arg, terminate = True)

		index += 1

	# create generator instance
	event_generator = SSD_Event_Generator(real_event_capture, simulate_event_capture, capture_duration, read_time, write_time, trim_time, concurrent_event)
	command_durt, activity = event_generator.capture_event()
	trim_simulator_utils.trim_simulator_export_event(command_durt, activity)


