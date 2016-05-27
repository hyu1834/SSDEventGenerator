## \file io_util.py
## @package io_util
# @author Hiu Hong Yu (AHMCT)
# @brief this modules contains functions for in and out stream.
# @details
#  Methods including:\n
#  <ul>
#  <li>output usage</li>
#  <li>output error</li>
#  <li>output logs</li>
#  </ul>
#

import sys
import os

## @brief standard usage out stream.
# @param message - message to output as usage
# @return None
def usage(message, terminate = False):
	sys.stderr.write("USAGE: %s\n" %(message))
	if terminate:
		sys.exit(1)

## @brief standard error out stream.
# @param message - message to output as error
# @return None
def stderr(message, terminate = False):
	sys.stderr.write('Error: %s\n'%(message))
	if terminate:
		sys.exit(1)

## @brief function error out stream.
# error output with location provided
# @param message - message to output as 
# @return None
def function_stderr(message,function_name):
	sys.stderr.write('Error: %s in %s\n'%(message,function_name))

## @brief standard warning out stream
# @param message - message to output as warning
# @return None
def warning(message):
	sys.stderr.write("WARNING: %s\n" %(message))

## @brief function warning out stream
# warning out stream with location provided
# @param message - message to output as warning
# @return None
def function_warning(message,function_name):
	sys.stderr.write("WARNING: %s in %s\n" %(message,function_name))

## @brief standard log out stream
# @param message - message to output as logs
# @return None
def stdlog(message):
	sys.stderr.write('%s\n'%(message))

## @brief status updater
# @param message - message to output as status
# @return None
def print_progress_status(message):
    sys.stdout.write('\r' + message)
    sys.stdout.flush()

