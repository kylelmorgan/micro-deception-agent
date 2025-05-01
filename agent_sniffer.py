import argparse
from scapy.all import *
from fake_services import deploy_fake_services_for_ip
from sql_deception import start_sql_honeypot
from deception_logger import log_event

# Track if the SQL honeypot is already running
sql_honeypot_started = False


# Parse command-line arguments
parser = argparse.ArgumentParser(description="Micro Deception Agent")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-a", "--active", action="store_true", help="Start deception immediately")
group.add_argument("-p", "--passive", action="store_true", help="Start deception after scan detection")
args = parser.parse_args()

known_ips = set()


def is_suspicious(pkt):
    global sql_honeypot_started

    if pkt.haslayer(IP) and pkt.haslayer(TCP):
        flags = str(pkt[TCP].flags)
        src = pkt[IP].src
        dport = pkt[TCP].dport

        if src not in known_ips:
            if flags == "":
                log_event("scan", src, f"NULL scan on port {dport}")
                deploy_fake_services_for_ip(src)
            elif flags == "F":
                log_event("scan", src, f"FIN scan on port {dport}")
                deploy_fake_services_for_ip(src)
            elif set(flags) >= set("FPU"):
                log_event("scan", src, f"XMAS scan on port {dport}")
                deploy_fake_services_for_ip(src)
            else:
                return False

            known_ips.add(src)

            if not sql_honeypot_started:
                start_sql_honeypot()
                sql_honeypot_started = True

            return True
    return False

def sniff_packets(pkt):
    is_suspicious(pkt)

if args.active:
    print("[+] Running in ACTIVE mode: deploying deception immediately.")
    log_event("startup", "127.0.0.1", "ACTIVE mode started")
    deploy_fake_services_for_ip("auto")  # Use placeholder IP for global deployment
    start_sql_honeypot()
    sql_honeypot_started = True
else:
    print("[*] Running in PASSIVE mode: waiting for scan detection...")
    log_event("startup", "127.0.0.1", "PASSIVE mode started")


sniff(filter="tcp", prn=sniff_packets, store=0, iface="ens37")
