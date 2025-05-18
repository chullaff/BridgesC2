import cmd
from .commands import list as cmd_list
from .commands import connect as cmd_connect
from .state import state

class BridgesMeshCLI(cmd.Cmd):
    intro = "BridgesC2 Operator CLI. Type help or ? to list commands.\n"
    prompt = "(bridgesc2) "

    def do_list(self, arg):
        "List all registered agents"
        cmd_list.cmd_list()

    def do_connect(self, arg):
        "Connect to an agent: connect <agent_id>"
        agent_id = arg.strip()
        if not agent_id:
            print("Usage: connect <agent_id>")
            return
        cmd_connect.cmd_connect(agent_id)

    def do_exit(self, arg):
        "Exit the CLI"
        print("Bye!")
        return True

    def do_EOF(self, arg):
        "Exit on Ctrl-D (EOF)"
        print()
        return True

    def emptyline(self):
        # Do nothing on empty input
        pass

if __name__ == "__main__":
    BridgesMeshCLI().cmdloop()
