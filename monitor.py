import argparse
import json
import logging
import os
import smtplib
import time
from dotenv import load_dotenv
from pyserverstatus import is_running
from threading import Timer
from functools import partial
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

# time constants
DAY = 86400
HOUR = 3600
MINUTE = 60
SECOND = 1

# email
error_count = 0
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
def _collect_receivers(file_path):
    receivers = []
    with open(file_path) as file:
        data = json.load(file)
        receivers = [receiver for receiver in data['receivers']]
    return receivers


def _send_email(send_from, send_to, subject, text, files=[], server="localhost", port=587, username='', password='', use_tls=False):
    logging.info("Sending email")

    message = MIMEMultipart()
    message['From'] = send_from
    message['To'] = COMMASPACE.join(send_to)
    message['Date'] = formatdate(localtime=True)
    message['Subject'] = subject
    message.attach(MIMEText(text))

    for file in files:
        with open(file, "rb") as file_bytes:
            part = MIMEApplication(file_bytes.read(), Name=basename(file))
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file)
            message.attach(part)

    smtp = smtplib.SMTP(server, port)
    if use_tls:
        smtp.starttls()
    if username and password:
        smtp.login(username, password) 
    smtp.sendmail(send_from, send_to, message.as_string())
    smtp.close()
    
def send_monitor_email(address, port):
    global receivers
    _send_email(
            send_from=os.getenv('SMTP_USER'),
            send_to=receivers,
            subject="Monitoring Alert",
            text=f"{address}:{port} is not running.",
            files=["./monitor.log"],
            server="smtp.gmail.com",
            port=587,
            username=os.getenv('SMTP_USER'),
            password=os.getenv('SMTP_PASSWORD'),
            use_tls=True
    )



# log status
def check_status(address, port, error_limit):
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
            send_monitor_email(address, port)
            

# main
if __name__ == '__main__':
    # load env variables
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("server_address", help="[required] server address for monitoring", type=str)
    parser.add_argument("--port", help="[optional] port number for server. default value is 80", default=80)
    parser.add_argument("--days", help="[optional] number of days from the checking server status interval. [default] value is 0", default=0)
    parser.add_argument("--hours", help="[optional] number of hours from the checking server status interval. [default] value is 0", default=0)
    parser.add_argument("--minutes", help="[optional] number of minutes from the checking server status interval. [default] value is 0", default=0)
    parser.add_argument("--seconds", help="[optional] number of seconds from the checking server status interval. [default] value is 1", default=1)
    parser.add_argument("--limit", help="[optional] number of errors logs that must be recorded before sending an email. [default] value is 5", default=5)
    args = parser.parse_args()
    
    # collect receivers
    receivers = _collect_receivers('receivers.json')

    interval = args.days * DAY + args.hours * HOUR + args.minutes * MINUTE + args.seconds * SECOND

    scheduler = Scheduler(interval, check_status, args=[args.server_address, args.port, args.limit])

    print("Starting monitor, press CTRL+C to stop.")

    scheduler.start()

    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            print("Monitor is shutting down...")
            scheduler.stop()
            break


