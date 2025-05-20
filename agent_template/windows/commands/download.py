import base64
import os

def run(params):
    """
    params = {
        "filepath": "/path/to/file"
    }
    """
    filepath = params.get("filepath")
    if not filepath or not os.path.isfile(filepath):
        return f"Файл не найден: {filepath}"

    try:
        with open(filepath, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        return f"Ошибка чтения файла: {e}"
