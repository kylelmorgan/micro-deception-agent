import csv
import os
from datetime import datetime

LOG_FILE = "deception_log.csv"

def log_event(event_type, ip_address, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "event_type", "ip_address", "details"])
        writer.writerow([timestamp, event_type, ip_address, details])