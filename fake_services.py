import socket
import threading
import random
from datetime import datetime

# Static service pool
SERVICE_POOL = {
    21: [b"220 vsFTPd 3.0.3\r\n", b"220 Pure-FTPd 1.0.49\r\n"],
    22: [b"SSH-2.0-OpenSSH_7.9p1\r\n", b"SSH-2.0-OpenSSH_9.9p1 Debian\r\n"],
    23: [b"Welcome to the Telnet server!\r\n"],
    25: [b"220 mail.fake-smtp.local ESMTP Postfix\r\n"],
    80: [b"HTTP/1.1 200 OK\r\nServer: Apache\r\n\r\n<h1>Fake Homepage</h1>"],
    3306: [b"\x00\x00\x00\x0a5.7.39-log\x00\x00\x00\x00"],
    3389: [b"RDP Protocol Initiated...\r\n"],
    8080: [b"HTTP/1.1 200 OK\r\nServer: nginx\r\n\r\n<h1>Welcome to nginx</h1>"],
}

# Track which IPs triggered deception
ip_deception_map = {}

def log_event(msg):
    with open("deception.log", "a") as f:
        f.write(f"{datetime.now()} | {msg}\n")

def handle_fake_service(port, banner):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("0.0.0.0", port))
        s.listen(1)
        print(f"[+] Fake service active on port {port}")
        while True:
            conn, addr = s.accept()
            print(f"[!] Connection from {addr[0]} to port {port}")
            log_event(f"Connection from {addr[0]} to fake port {port}")
            conn.sendall(banner)
            conn.close()
    except Exception as e:
        print(f"[x] Failed to bind port {port}: {e}")

def deploy_fake_services_for_ip(src_ip, count=3):
    if src_ip in ip_deception_map:
        print(f"[~] {src_ip} already triggered deception.")
        return

    chosen_ports = random.sample(list(SERVICE_POOL.keys()), count)
    ip_deception_map[src_ip] = chosen_ports
    log_event(f"Deploying fake services for {src_ip} on ports {chosen_ports}")

    for port in chosen_ports:
        banner = random.choice(SERVICE_POOL[port])
        t = threading.Thread(target=handle_fake_service, args=(port, banner))
        t.daemon = True
        t.start()

    print(f"[+] Deception deployed for {src_ip} on ports: {', '.join(str(p) for p in chosen_ports)}")
