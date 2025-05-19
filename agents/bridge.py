import asyncio
from agents.base import BaseAgent
from agents.comms.mesh import MeshComms
from shared.messages import Message
from shared.routing import calculate_route

class BridgeAgent(BaseAgent):
    def __init__(self, agent_id, listen_port, known_peers):
        self.agent_id = agent_id
        self.hostname = None
        self.platform = None
        self.running = True
        self.pending_responses = {}

        self.mesh = MeshComms(agent_id, listen_port, known_peers)
        self.mesh.message_handler = self.handle_mesh_message

    async def start(self):
        await asyncio.gather(
            self.mesh.start_server(),
            self.heartbeat_loop()
        )

    async def handle_mesh_message(self, payload):
        """
        Обработка сообщений, полученных по mesh.
        Добавлена поддержка обновления списка пиров.
        """
        msg_type = payload.get("type")

        if msg_type == "peer_update":
            peer_id = payload.get("peer_id")
            ip = payload.get("ip")
            port = payload.get("port")
            if peer_id and ip and port:
                self.register_new_peer(peer_id, ip, port)
                # После добавления можно по желанию распространить обновление дальше
                await self.broadcast_peer_update(peer_id, ip, port)
        else:
            # Передаем остальные типы сообщений в базовый обработчик
            await self.process_payload(payload)

    async def send_via_route(self, destination_id, payload):
        route = calculate_route(self.agent_id, destination_id, self.mesh.known_peers)
        if not route:
            print(f"[{self.agent_id}] Маршрут до {destination_id} не найден")
            return
        msg = Message(route=route, payload=payload)
        await self.mesh.send_along_route(msg)

    async def heartbeat_loop(self):
        while True:
            to_remove = []
            for peer_id, (ip, port) in self.mesh.known_peers.items():
                try:
                    ping_payload = {"type": "ping", "from": self.agent_id}
                    msg = Message(route=[self.agent_id, peer_id], payload=ping_payload)
                    await self.mesh.send_message(ip, port, msg)
                except Exception as e:
                    print(f"[{self.agent_id}] Не удалось отправить ping {peer_id}: {e}")
            await asyncio.sleep(15)

    def register_new_peer(self, peer_id, ip, port):
        """
        Добавляет или обновляет известного пира.
        """
        if peer_id not in self.mesh.known_peers:
            print(f"[{self.agent_id}] Новый peer добавлен: {peer_id} ({ip}:{port})")
        else:
            print(f"[{self.agent_id}] Обновление peer: {peer_id} ({ip}:{port})")
        self.mesh.known_peers[peer_id] = (ip, port)

    async def broadcast_peer_update(self, peer_id, ip, port):
        """
        Рассылает всем известным пирами информацию о новом пире.
        """
        payload = {
            "type": "peer_update",
            "peer_id": peer_id,
            "ip": ip,
            "port": port,
        }

        for known_peer_id, (peer_ip, peer_port) in self.mesh.known_peers.items():
            if known_peer_id == self.agent_id or known_peer_id == peer_id:
                # Не отправляем самому себе и источнику обновления
                continue
            route = calculate_route(self.agent_id, known_peer_id, self.mesh.known_peers)
            if not route:
                continue
            msg = Message(route=route, payload=payload)
            try:
                await self.mesh.send_along_route(msg)
            except Exception as e:
                print(f"[{self.agent_id}] Ошибка рассылки обновления peer {known_peer_id}: {e}")
