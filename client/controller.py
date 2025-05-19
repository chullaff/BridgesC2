import requests
from shared.config import SERVER_URL

API_URL = f"{SERVER_URL}/api"

class Controller:
    def __init__(self, api_url=API_URL):
        self.api_url = api_url

    def list_agents(self):
        resp = requests.get(f"{self.api_url}/agents/")
        resp.raise_for_status()
        return resp.json()

    def register_agent(self, name, ip=None):
        data = {"name": name, "ip": ip}
        resp = requests.post(f"{self.api_url}/agents/", params=data)
        resp.raise_for_status()
        return resp.json()

    def create_task(self, agent_id: str, command: str):
        data = {"agent_id": agent_id, "command": command}
        resp = requests.post(f"{self.api_url}/tasks/", params=data)
        resp.raise_for_status()
        return resp.json()
