import socket
import asyncio
from utils.config import SERVER_URL, AGENT_NAME
from comms.mesh import MeshComms
# from base_agent import BaseAgent
# import threading

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    agent_id = AGENT_NAME
    # agent = BaseAgent()

    # asyncio.run(agent.run())
    port = 9001  # Или любой свободный порт

    # Инициализация MeshComms (регистрирует себя и запускает сервер)
    comms = MeshComms(agent_id, port, bootstrap_url=SERVER_URL + "/api")
    asyncio.run(comms.start())

