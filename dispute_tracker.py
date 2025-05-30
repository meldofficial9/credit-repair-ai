import csv
import os
from datetime import datetime, timedelta

TRACKER_FILE = "disputes.csv"

def log_dispute(bureau, account_name, round_num):
    if not os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["bureau", "account", "round", "date_sent"])

    with open(TRACKER_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([bureau, account_name, round_num, datetime.now().strftime("%Y-%m-%d")])

def get_last_dispute_info(bureau, account_name):
    if not os.path.exists(TRACKER_FILE):
        return None

    with open(TRACKER_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        records = [row for row in reader if row["bureau"] == bureau and row["account"] == account_name]
        if not records:
            return None
        latest = sorted(records, key=lambda r: r["date_sent"], reverse=True)[-1]
        return {
            "round": int(latest["round"]),
            "date_sent": datetime.strptime(latest["date_sent"], "%Y-%m-%d")
        }

def needs_follow_up(bureau, account_name):
    info = get_last_dispute_info(bureau, account_name)
    if not info:
        return False
    days_since = (datetime.now() - info["date_sent"]).days
    return days_since >= 30  # Ready for next round
