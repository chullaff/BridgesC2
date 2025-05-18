class State:
    def __init__(self):
        self.active_agent_id = None
        self.active_agent_name = None

    def set_active_agent(self, agent_id: str, agent_name: str):
        self.active_agent_id = agent_id
        self.active_agent_name = agent_name

    def clear_active_agent(self):
        self.active_agent_id = None
        self.active_agent_name = None

    def get_active_agent(self):
        return self.active_agent_id, self.active_agent_name


state = State()
