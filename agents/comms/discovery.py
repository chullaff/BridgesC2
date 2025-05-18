import socket
import struct
import threading
import time

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
BROADCAST_INTERVAL = 5

class DiscoveryService:
    def __init__(self, agent_id, listen_port, on_peer_discovered):
        self.agent_id = agent_id
        self.listen_port = listen_port
        self.on_peer_discovered = on_peer_discovered
        self.running = False

    def _listener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', MCAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                msg = data.decode()
                # Ожидаем сообщение вида "agent_id:agent_ip:agent_port"
                parts = msg.split(":")
                if len(parts) == 3 and parts[0] != self.agent_id:
                    peer_id, peer_ip, peer_port = parts[0], parts[1], int(parts[2])
                    self.on_peer_discovered(peer_id, peer_ip, peer_port)
            except Exception:
                pass

    def _broadcaster(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        ttl = struct.pack('b', 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        msg = f"{self.agent_id}:{self._get_ip()}:{self.listen_port}".encode()

        while self.running:
            sock.sendto(msg, (MCAST_GRP, MCAST_PORT))
            time.sleep(BROADCAST_INTERVAL)

    def _get_ip(self):
        # Простая функция для получения IP локальной машины
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def start(self):
        self.running = True
        threading.Thread(target=self._listener, daemon=True).start()
        threading.Thread(target=self._broadcaster, daemon=True).start()

    def stop(self):
        self.running = False
