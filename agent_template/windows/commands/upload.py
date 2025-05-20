import base64
import os

def run(params):
    """
    params = {
        "filepath": "/path/to/save/file",
        "content": "<base64-encoded content>"
    }
    """
    filepath = params.get("filepath")
    content_b64 = params.get("content")

    if not filepath or not content_b64:
        return "Недостаточно параметров: filepath и content обязательны"

    try:
        content = base64.b64decode(content_b64)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(content)
        return f"Файл сохранён: {filepath}"
    except Exception as e:
        return f"Ошибка записи файла: {e}"
