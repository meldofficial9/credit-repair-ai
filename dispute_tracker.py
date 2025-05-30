import csv
import os
from datetime import datetime

TRACKER_FILE = "disputes.csv"

def log_dispute(bureau, account_name, round_num):
    if not os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["bureau", "account", "round", "date_sent"])

    with open(TRACKER_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([bureau, account_name, round_num, datetime.now().strftime("%Y-%m-%d")])

def has_dispute_been_sent(bureau, account_name):
    if not os.path.exists(TRACKER_FILE):
        return False

    with open(TRACKER_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["bureau"] == bureau and row["account"] == account_name:
                return True
    return False