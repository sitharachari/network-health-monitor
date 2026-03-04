# Network Health Monitor

A Python tool that monitors the availability of hosts and IP addresses on a network. It pings each host on a scheduled interval, logs results to a local database, sends email alerts when a host goes down or comes back online, and delivers a daily uptime summary report.

---

## Features

- Pings hosts on a configurable schedule (default: every 5 minutes)
- Logs all results to a local SQLite database
- Sends email alerts only when a host status changes
- Generates and emails a daily uptime percentage report
- Hosts managed via a simple CSV file — no code changes needed to add or remove targets

---

## Project Structure

```
network-health-monitor/
├── monitor.py       # Main script
├── hosts.csv        # List of hosts to monitor
├── requirements.txt # Python dependencies
├── .env             # Credentials (not committed)
├── .gitignore
└── README.md
```

---

## Setup

**1. Clone the repo:**
```bash
git clone https://github.com/yourusername/network-health-monitor.git
cd network-health-monitor
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Create your `.env` file:**
```
EMAIL_SENDER=your.email@gmail.com
EMAIL_RECEIVER=your.email@gmail.com
EMAIL_PASSWORD=your_google_app_password
```

> To generate a Google App Password: Google Account → Security → 2-Step Verification → App Passwords

**4. Edit `hosts.csv` with the hosts you want to monitor:**
```csv
Name,Address
Google DNS,8.8.8.8
Cloudflare DNS,1.1.1.1
Local Router,192.168.1.1
```

**5. Run:**
```bash
python monitor.py
```

---

## Configuration

All settings are at the top of `monitor.py`:

| Variable | Default | Description |
|---|---|---|
| `CHECK_INTERVAL` | `5` | Minutes between checks |
| `REPORT_TIME` | `"08:00"` | Time to send daily report |
| `DB_FILE` | `"monitor.db"` | SQLite database file |
| `HOSTS_FILE` | `"hosts.csv"` | Hosts input file |

---

## How It Works

1. On startup, the script initializes the SQLite database and runs an immediate check
2. Every `CHECK_INTERVAL` minutes it pings all hosts in `hosts.csv`
3. Each result is logged to `monitor.db` with a timestamp
4. If a host changes status (online → offline or vice versa), an email alert is sent immediately
5. Every day at `REPORT_TIME`, a uptime summary is emailed with uptime percentages per host

---

## Dependencies

- `schedule` — task scheduling
- `python-dotenv` — loading credentials from `.env`

All others (`sqlite3`, `smtplib`, `subprocess`, `csv`) are part of the Python standard library.