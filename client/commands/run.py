from ..controller import Controller
from ..state import state

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
        print(f"Task created: {task['id']} for agent {agent_name} ({agent_id})")
    except Exception as e:
        print(f"Failed to create task: {e}")
