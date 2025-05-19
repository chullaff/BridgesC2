import asyncio
from shared.messages import Message
from agents.crypto import encrypt, decrypt

class MeshComms:
    def __init__(self, agent_id, listen_port, known_peers):
        self.agent_id = agent_id
        self.listen_port = listen_port
        self.known_peers = known_peers  # agent_id -> (ip, port)
        self.message_handler = None
        self.processed_msgs = set()  # msg_id для защиты от повторов

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
                # Повторное сообщение — игнорируем
                writer.close()
                await writer.wait_closed()
                return

            self.processed_msgs.add(msg.msg_id)

            if msg.route[-1] == self.agent_id:
                # Сообщение для нас
                if self.message_handler:
                    await self.message_handler(msg.payload)
            else:
                # Сообщение нужно переслать дальше
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
