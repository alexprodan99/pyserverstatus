import argparse
import logging
import smtplib
import time
from pyserverstatus import is_running
from threading import Timer
from functools import partial

# time constants
DAY = 86400
HOUR = 3600
MINUTE = 60
SECOND = 1

# email
error_count = 0
sender = 'localmonitor@monitor.com'
receivers = []

# logging
fmtstr = '%(asctime)s [%(levelname)s] %(message)s'
datestr = '%m/%d/%Y %I:%M:%S %p'
logging.basicConfig(filename="monitor.log", level=logging.INFO, filemode="w", format=fmtstr, datefmt=datestr)

# scheduler
class Scheduler(object):
    def __init__(self, interval, function, args=[], kwargs={}):
        """
        Runs the function at a specified interval with given arguments.
        """
        self.interval = interval
        self.function = partial(function, *args, **kwargs)
        self.running  = False 
        self._timer   = None 

    def __call__(self):
        """
        Handler function for calling the partial and continuting. 
        """
        self.running = False  # mark not running
        self.start()          # reset the timer for the next go 
        self.function()       # call the partial function 

    def start(self):
        """
        Starts the interval and lets it run. 
        """
        if self.running:
            # Don't start if we're running! 
            return 
            
        # Create the timer object, start and set state. 
        self._timer = Timer(self.interval, self)
        self._timer.start() 
        self.running = True

    def stop(self):
        """
        Cancel the interval (no more function calls).
        """
        if self._timer:
            self._timer.cancel() 
        self.running = False 
        self._timer  = None


# send email
def send_email():
    global sender
    global receivers
    logging.info("Sending email")
    


# log status
def log_status(address, port, error_limit):
    global error_count
    if is_running(address, port):
        logging.info(f"{address}:{port} is running")
        error_count = 0
    else:
        logging.error(f"{address}:{port} is not running")
        if error_count < error_limit:
            error_count += 1
        else:
            error_count = 0
            send_email()

# main
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("server_address", help="[required] server address for monitoring", type=str)
    parser.add_argument("--port", help="[optional] port number for server. default value is 80", default=80)
    parser.add_argument("--days", help="[optional] number of days from the checking server status interval. [default] value is 0", default=0)
    parser.add_argument("--hours", help="[optional] number of hours from the checking server status interval. [default] value is 0", default=0)
    parser.add_argument("--minutes", help="[optional] number of minutes from the checking server status interval. [default] value is 0", default=0)
    parser.add_argument("--seconds", help="[optional] number of seconds from the checking server status interval. [default] value is 1", default=1)
    parser.add_argument("--limit", help="[optional] number of errors logs that must be recorded before sending an email. [default] value is 5", default=5)
    args = parser.parse_args()
    
    interval = args.days * DAY + args.hours * HOUR + args.minutes * MINUTE + args.seconds * SECOND

    scheduler = Scheduler(interval, log_status, args=[args.server_address, args.port, args.limit])

    print("Starting monitor, press CTRL+C to stop.")

    scheduler.start()

    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            print("Monitor is shutting down...")
            scheduler.stop()
            break


