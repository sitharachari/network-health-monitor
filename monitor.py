from dotenv import load_dotenv
import os
import platform 
import subprocess
import csv
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import schedule
import time 



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

def send_email(subject, body):
    """Send an email alert via Gmail."""
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = EMAIL_RECEIVER

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        print(f"  → Email sent: {subject}")
    except Exception as e:
        print(f"  → Email failed: {e}")


def send_alert(name, address, status):
    subject = f"[Monitor] ALERT: {name} is {status}"
    body = (
        f"Host:    {name}\n"
        f"Address: {address}\n"
        f"Status:  {status}\n"
        f"Time:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    send_email(subject, body)

# Tracks the last known status of each host so we only alert on changes
previous_status = {}

def check_hosts():
    """Ping all hosts, log results, and send alerts on status changes."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking hosts...")
    hosts = load_hosts()

    for host in hosts:
        name    = host["Name"]
        address = host["Address"]
        status  = "ONLINE" if ping(address) else "OFFLINE"

        # Log every result to the database
        log_result(name, address, status)

        # Only send an alert if the status changed since last check
        if name in previous_status and previous_status[name] != status:
            send_alert(name, address, status)

        previous_status[name] = status

        # Colour-coded console output
        colour = "\033[92m" if status == "ONLINE" else "\033[91m"  # green / red
        reset  = "\033[0m"
        print(f"  {colour}{status}{reset}  {name} ({address})")

def daily_report():
    """Query the DB and email a summary of uptime percentages."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            name,
            address,
            SUM(CASE WHEN status = 'ONLINE'  THEN 1 ELSE 0 END) AS up,
            SUM(CASE WHEN status = 'OFFLINE' THEN 1 ELSE 0 END) AS down
        FROM logs
        GROUP BY name, address
    """)
    rows = cursor.fetchall()
    conn.close()

    report = "Daily Uptime Report\n" + "=" * 40 + "\n"
    for name, address, up, down in rows:
        total      = up + down
        pct        = (up / total * 100) if total > 0 else 0
        report    += f"{name} ({address}): {pct:.1f}% uptime  ({up} up / {down} down)\n"

    print("\n" + report)
    send_email("Daily Uptime Report", report)

# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("Network Health Monitor starting...")

    # Set up the database
    init_db()

    # Run an immediate check on startup
    check_hosts()

    # Schedule recurring checks
    schedule.every(CHECK_INTERVAL).minutes.do(check_hosts)

    # Schedule daily report
    schedule.every().day.at(REPORT_TIME).do(daily_report)

    print(f"\nMonitor running — checking every {CHECK_INTERVAL} minutes.")
    print("Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(1)
