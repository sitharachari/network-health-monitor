from dotenv import load_dotenv
import os
import platform 
import subprocess
import csv

load_dotenv()

EMAIL_SENDER   = os.getenv("EMAIL_SENDER")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
HOSTS_FILE     = "hosts.csv"
DB_FILE        = "monitor.db"
LOG_FILE       = "monitor.log"
CHECK_INTERVAL = 5   # minutes between checks
REPORT_TIME    = "08:00"  # time to send daily report



def ping(address):
    """Returns True if host is reachable, False otherwise."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    result = subprocess.run(
        ["ping", param, "1", address],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

def load_hosts():
    """Read hosts from hosts.csv and return as list of dicts."""
    hosts = []
    with open(HOSTS_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hosts.append(row)
    return hosts

