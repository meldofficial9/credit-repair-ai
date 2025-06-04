import csv
import os
from datetime import datetime, timedelta

# This function will dynamically generate the filename based on username
TRACKER_FILE_TEMPLATE = "disputes_{username}.csv"

def get_tracker_file(username):
    return TRACKER_FILE_TEMPLATE.format(username=username)

def log_dispute(username, bureau, account_name, round_num):
    tracker_file = get_tracker_file(username)
    if not os.path.exists(tracker_file):
        with open(tracker_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["bureau", "account", "round", "date_sent"])

    with open(tracker_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([bureau, account_name, round_num, datetime.now().strftime("%Y-%m-%d")])

def get_last_dispute_info(username, bureau, account_name):
    tracker_file = get_tracker_file(username)
    if not os.path.exists(tracker_file):
        return None

    with open(tracker_file, mode="r") as file:
        reader = csv.DictReader(file)
        records = [row for row in reader if row["bureau"] == bureau and row["account"] == account_name]
        if not records:
            return None
        latest = sorted(records, key=lambda r: r["date_sent"], reverse=True)[-1]
        return {
            "round": int(latest["round"]),
            "date_sent": datetime.strptime(latest["date_sent"], "%Y-%m-%d")
        }

def needs_follow_up(username, bureau, account_name):
    info = get_last_dispute_info(username, bureau, account_name)
    if not info:
        return False
    days_since = (datetime.now() - info["date_sent"]).days
    return days_since >= 30  # Ready for next round

def get_all_followups(username):
    tracker_file = get_tracker_file(username)
    if not os.path.exists(tracker_file):
        return []

    with open(tracker_file, mode="r") as file:
        reader = csv.DictReader(file)
        seen = set()
        followups = []
        for row in reader:
            key = (row["bureau"], row["account"])
            if key in seen:
                continue
            seen.add(key)
            if needs_follow_up(username, row["bureau"], row["account"]):
                followups.append(row)
        return followups

