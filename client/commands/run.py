from ..controller import Controller
from ..state import state
import time
import requests

def cmd_run(command: str):
    if not command.strip():
        print("Usage: run <command>")
        return
    
    agent_id, agent_name = state.get_active_agent()
    if not agent_id:
        print("No active agent selected. Use 'connect' to select an agent.")
        return

    ctrl = Controller()
    try:
        task = ctrl.create_task(agent_id, command)
        task_id = task['id']
        print(f"Task created: {task['id']} for agent {agent_name} ({agent_id})")

        print('[*] Waiting fot agent to respond...')

        # Простой polling (ожидание овтета с таймаутом)
        for _ in range(10):
            time.sleep(2)
            try:
                result = ctrl.get_result(task_id)
                if result and result['output']:
                    print(f'[*] Result:\n{result['output']}')
                    return
            except requests.HTTPError:
                pass
        print('[!] Timeout: No result received.')
    except Exception as e:
        print(f"Failed to create task: {e}")
