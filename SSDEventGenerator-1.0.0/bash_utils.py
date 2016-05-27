## @package bash_module
# Documentation for bash module.
# this modules contains all the functions for executeing bash command through python
# More details.
# global function for executing bash command
import sys, os
import logging
from sys import platform as _platform
import subprocess
import signal

sys.path.insert(0, './alarm')
import timeout_alarm as ta

# Documentation for execute_bash_command
# run the command line, and see if there is any erorr
# More details.
# function take in 2 arguements.\n
# CMD and timeout\n.
# function will subprocess bash command line, if time reaches and no result return\n
# function time out, bash command execute unsuccessfully.\n
# Arguements:\n
# \tcmd - bash command line\n
# \ttimeout - timeout time (ms)
def execute_bash_command(cmd,timeout):
	signal.signal(signal.SIGALRM,ta.timeout_alarm_handler)
	signal.alarm(timeout)	#30 seconds
	try:
		#subprocess the bash command
		shell_command = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output_message,error_message = shell_command.communicate()
		error_code = shell_command.wait()

		#if there is any error code, signal the alarm, print error, and return execute bash unsuccessfully
		if error_code:
			signal.alarm(0)
			print('Shell command failed <%s>: %s' % (error_code,error_message))
			return False,error_message
		signal.alarm(0)

	except ta.Timeout_Alarm:
		print('Shell command: %s timeout from executing %ds'%(cmd,timeout))
		return False,error_message

	return True,output_message