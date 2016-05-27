import signal

class Timeout_Alarm(Exception):
    pass

def timeout_alarm_handler(signum,frame):
    raise Timeout_Alarm