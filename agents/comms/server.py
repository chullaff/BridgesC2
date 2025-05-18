import requests
from ..crypto import encrypt, decrypt

API_URL = "http://localhost:8000/api"

class ServerComm:
    def __init__(self, agent_id=None):
        self.agent_id = agent_id

    def register(self, name, ip=None):
        data = {"name": name, "ip": ip}
        resp = requests.post(f"{API_URL}/agents/", params=data)
        resp.raise_for_status()
        res = resp.json()
        self.agent_id = res.get("id")
        return res

    def get_tasks(self):
        if not self.agent_id:
            raise Exception("Agent not registered")
        resp = requests.get(f"{API_URL}/tasks/{self.agent_id}")
        resp.raise_for_status()
        # Ожидаем зашифрованный ответ
        encrypted = resp.json().get("data")
        if not encrypted:
            return []
        tasks = decrypt(encrypted)
        return tasks

    def send_result(self, task_id, result_data):
        if not self.agent_id:
            raise Exception("Agent not registered")
        encrypted = encrypt(result_data)
        data = {"agent_id": self.agent_id, "task_id": task_id, "result": encrypted}
        resp = requests.post(f"{API_URL}/results/", json=data)
        resp.raise_for_status()
        return resp.json()
