import asyncio
from agents.base import BaseAgent
from agents.comms.mesh import MeshComms
from shared.messages import Message
from shared.routing import calculate_route

class BridgeAgent(BaseAgent):
    def __init__(self, agent_id, listen_port, known_peers):
        super().__init__(agent_id)
        self.mesh = MeshComms(agent_id, listen_port, known_peers)
        self.mesh.message_handler = self.handle_mesh_message
        self.known_peers = known_peers  # Можно обновлять динамически

    async def start(self):
        # Запускаем mesh-сервер + базовый агент
        await asyncio.gather(
            self.mesh.start_server(),
            self.heartbeat_loop()
        )

    async def handle_mesh_message(self, payload):
        """
        Получает расшифрованное сообщение с mesh-уровня и передаёт в базовый обработчик.
        """
        await self.process_payload(payload)

    async def send_via_route(self, destination_id, payload):
        """
        Строит маршрут и оборачивает сообщение, затем отправляет через mesh.
        Если маршрут не найден — логирует ошибку.
        """
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
                    # Можно пометить пира для удаления или повторной проверки
                    # to_remove.append(peer_id)
            # for peer_id in to_remove:
            #     self.mesh.known_peers.pop(peer_id, None)
            await asyncio.sleep(15)

    def register_new_peer(self, peer_id, ip, port):
        """
        Добавляет или обновляет известного пира.
        """
        self.mesh.known_peers[peer_id] = (ip, port)
        print(f"[{self.agent_id}] Добавлен/обновлен peer: {peer_id} ({ip}:{port})")
