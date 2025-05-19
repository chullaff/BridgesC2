import os

# URL сервера (можно менять через переменную окружения)
SERVER_URL = os.getenv("BRIDGESMESH_SERVER_URL", "http://192.168.1.74:8000")

# Порт, на котором агенты будут слушать mesh-сообщения по умолчанию
MESH_LISTEN_PORT = int(os.getenv("BRIDGESMESH_MESH_PORT", "9000"))

# Таймауты и интервалы
TASK_FETCH_INTERVAL = int(os.getenv("BRIDGESMESH_TASK_FETCH_INTERVAL", "5"))  # секунды
HEARTBEAT_INTERVAL = int(os.getenv("BRIDGESMESH_HEARTBEAT_INTERVAL", "15"))  # секунды

# Ключи для шифрования (в реальном проекте — загружать из безопасного хранилища)
ENCRYPTION_KEY = os.getenv("BRIDGESMESH_ENCRYPTION_KEY", "my-secret-key-12345")

# Логирование
LOG_LEVEL = os.getenv("BRIDGESMESH_LOG_LEVEL", "INFO")

# Максимальный размер сообщения (байт)
MAX_MESSAGE_SIZE = int(os.getenv("BRIDGESMESH_MAX_MESSAGE_SIZE", "65536"))
