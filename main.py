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
    pc.printout("-"*80)
    pc.printout("\nWelcome to the VK scraper\n")
    pc.printout("Remember to praise the sun and follow the instructions\n")
    pc.printout("Alpha Build - Developed by Alberto Federico Olivieri\n\n", pc.CYAN)
    pc.printout("Type 'list' to show all allowed commands\n")
    pc.printout("-" * 80)


def cmdlist():
    pc.printout("credentials\t")
    pc.printout("Insert Username, Password, and API Key", colour=pc.YELLOW)
    pc.printout("targets\t")
    pc.printout("Insert comma separated list of target(s)", colour=pc.YELLOW)
    pc.printout("dates\t")
    pc.printout("Insert date or date range", colour=pc.YELLOW)


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


signal.signal(signal.SIGINT, signal_handler)
if is_windows:
    pyreadline.Readline().parse_and_bind("tab: complete")
    pyreadline.Readline().set_completer(completer)
else:
    gnureadline.parse_and_bind("tab: complete")
    gnureadline.set_completer(completer)

welcome()

parser = argparse.ArgumentParser(description="Description")
parser.add_argument('targets', type=str,
                    help='target identificator, single or comma separated list')

args = parser.parse_args()

api = VkApiWrapper(args.targets)


commands = {
    'list':             cmdlist,
    'help':             cmdlist,
    'quit':             _quit,
    'exit':             _quit,
    'credentials':      api.store_credentials,
    'tagrets':          api.set_targets,
    'date':             api.set_date,
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
