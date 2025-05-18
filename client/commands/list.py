from ..controller import Controller
from ..state import state

def cmd_list():
    ctrl = Controller()
    agents = ctrl.list_agents()
    if not agents:
        print("No agents found.")
        return
    print("Available agents:")
    for a in agents:
        active_marker = " (active)" if state.active_agent_id == a['id'] else ""
        print(f"  {a['id']} - {a['name']} [{a['ip']}] {active_marker}")
