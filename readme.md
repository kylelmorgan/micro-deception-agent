# Micro Deception Agent

A lightweight network deception tool and honeypot built in Python.  
It detects hostile scans, deploys fake services, simulates vulnerable systems, and traps attackers with deceptive content like fake login portals, file repositories, and SQL injection honeypots.

Designed for cybersecurity education, threat research, and blue team defensive exercises.

## Features

- Passive Mode: Waits for a network scan before deploying fake services
- Active Mode: Instantly starts deception techniques at program launch
- Fake Open Ports: Random services (SSH, FTP, MySQL, RDP, etc.)
- SQL Injection Honeypot: Detects blind SQLi attempts, injects fake delays and errors
- Fake File Repository: Lets attackers download convincing fake data after login
- Fake Login Portal: Accepts only common weak passwords (top 100 list)
- Unified CSV Logging: Tracks scans, login attempts, file downloads, and SQLi probes
- Easily Filterable Logs: Perfect for SIEM ingestion, Excel analysis, or forensic review

## Requirements

- Python 3.8+
- pip packages:


Tested on:

- Ubuntu 22.04 LTS Server (Victim VM)
- Kali Linux (Attacker VM)

## Installation

1. Clone this repository:
https://github.com/kylelmorgan/micro-deception-agent.git


2. Install dependencies:

pip3 install -r requirements.txt

3. (Optional) Edit `common_passwords.txt` to customize accepted login credentials.

## Usage

### Passive Mode (Deploy deception after detecting a scan)

sudo python3 agent_sniffer.py -p


- Waits silently until hostile scanning activity is detected.
- Then launches fake services and SQL injection honeypots.

### Active Mode (Deploy deception immediately)

sudo python3 agent_sniffer.py -a


- Instantly launches fake ports and web honeypots at startup.
- Useful for lab demonstrations or proactive traps.

## Project Structure

| File                  | Purpose                                           |
|-----------------------|---------------------------------------------------|
| `agent_sniffer.py`    | Main sniffer and controller                      |
| `fake_services.py`    | Deploys fake open ports and service banners      |
| `sql_deception.py`    | Fake login portal, fake files, SQLi honeypot     |
| `deception_logger.py` | Centralized CSV logger for all events            |
| `common_passwords.txt`| Passwords accepted for login deception           |
| `fake_files/`         | Folder containing downloadable fake files        |
| `deception_log.csv`   | Log file (timestamped CSV format)                |

## Example Log (deception_log.csv)

timestamp,event_type,ip_address,details 
2025-04-11 23:20:15,scan,192.168.56.102,NULL scan on port 80 
2025-04-11 23:20:17,deception,192.168.56.102,Fake services deployed on ports 22, 80, 3306 
2025-04-11 23:20:22,login_fail,192.168.56.102,user='admin' pass='hunter2' 
2025-04-11 23:20:28,login_success,192.168.56.102,user='admin' pass='123456' 
2025-04-11 23:20:35,download,192.168.56.102,filename='passwords.csv' 
2025-04-11 23:20:40,sqli,192.168.56.102,query='admin' or sleep(5)-- delay=4.3s error='Uncaught mysqli_sql_exception: Commands out of sync...'

