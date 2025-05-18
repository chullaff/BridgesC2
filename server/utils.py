import uuid
import logging

def generate_id() -> str:
    return str(uuid.uuid4())

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

def log_info(msg: str):
    logging.info(msg)
