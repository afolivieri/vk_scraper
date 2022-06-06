#!/usr/bin/env python3


from src import printcolors as pc
from src.vk_wrapper import VkApiWrapper
import argparse
import sys
import signal

is_windows = False

try:
    import gnureadline
except:
    is_windows = True
    import pyreadline


def welcome():
    pc.printout("-" * 80)
    pc.printout(" _   _ _   __  _____                                \n", pc.GREEN)
    pc.printout("| | | | | / / /  ___|                               \n", pc.GREEN)
    pc.printout("| | | | |/ /  \ `--.  ___ _ __ __ _ _ __   ___ _ __ \n", pc.GREEN)
    pc.printout("| | | |    \   `--. \/ __| '__/ _` | '_ \ / _ \ '__|\n", pc.GREEN)
    pc.printout("\ \_/ / |\  \ /\__/ / (__| | | (_| | |_) |  __/ |   \n", pc.GREEN)
    pc.printout(" \___/\_| \_/ \____/ \___|_|  \__,_| .__/ \___|_|   \n", pc.GREEN)
    pc.printout("                                   | |              \n", pc.GREEN)
    pc.printout("                                   |_|              \n", pc.GREEN)
    print("\n")
    pc.printout("Code structure based on OSINTagram\n", pc.YELLOW)
    pc.printout("Alpha Build - Developed by Alberto Federico Olivieri\n\n", pc.CYAN)
    pc.printout("Type 'list' to show all allowed commands\n")
    pc.printout("-" * 80)


def cmdlist():
    pc.printout("config\t\t")
    pc.printout("Insert Username, Password, and API Key\n", colour=pc.YELLOW)
    pc.printout("dates\t\t")
    pc.printout("Insert date or date range\n", colour=pc.YELLOW)
    pc.printout("targets\t\t")
    pc.printout("Insert whitespace separated list of target(s), will overwrite old ones\n", colour=pc.YELLOW)
    pc.printout("tshow\t\t")
    pc.printout("Show comma separated list of target(s)\n", colour=pc.YELLOW)



def signal_handler(sig, frame):
    pc.printout("\nGoodbye!\n", pc.RED)
    sys.exit(0)


def completer(text, state):
    options = [i for i in commands if i.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None


def _quit():
    pc.printout("Goodbye!\n", pc.RED)
    sys.exit(0)


welcome()

parser = argparse.ArgumentParser(description="Description")
parser.add_argument('targets', type=str, nargs='+',
                    help='target identificator, single or whitespace separated list')

args = parser.parse_args()

api = VkApiWrapper(args.targets)


commands = {
    'list':             cmdlist,
    'help':             cmdlist,
    'quit':             _quit,
    'exit':             _quit,
    'credentials':      api.store_credentials,
    'dates':            api.set_dates,
    'targets':          api.set_targets,
    'tshow':            api.show_targets
}

signal.signal(signal.SIGINT, signal_handler)
if is_windows:
    pyreadline.Readline().parse_and_bind("tab: complete")
    pyreadline.Readline().set_completer(completer)
else:
    gnureadline.parse_and_bind("tab: complete")
    gnureadline.set_completer(completer)

while True:
    pc.printout("Run a command: ", pc.YELLOW)
    cmd = input()

    _cmd = commands.get(cmd)

    if _cmd:
        _cmd()
    elif cmd == "":
        print("")
    else:
        pc.printout("Unknown command\n", pc.RED)
