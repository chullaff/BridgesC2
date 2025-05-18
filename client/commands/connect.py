from ..controller import Controller
from ..state import state

def cmd_connect(agent_id: str):
    ctrl = Controller()
    agents = ctrl.list_agents()
    for a in agents:
        if a['id'] == agent_id:
            state.set_active_agent(agent_id, a['name'])
            print(f"Connected to agent {a['name']} ({agent_id})")
            return
    print(f"Agent {agent_id} not found.")
