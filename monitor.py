from dotenv import load_dotenv
import os
import platform 
import subprocess
import csv
import sqlite3
from datetime import datetime


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

def init_db():
    """Create the logs table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT,
            address   TEXT,
            status    TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_result(name, address, status):
    """Insert a ping result into the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (name, address, status, timestamp) VALUES (?, ?, ?, ?)",
        (name, address, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


