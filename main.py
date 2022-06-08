#!/usr/bin/env python3


from src import printcolors as pc
from src.vk_wrapper import VkApiWrapper
import argparse
import sys
import signal


def welcome() -> None:
    pc.printout("-" * 80 + "\n")
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
    pc.printout("This program will create a csv with the date, text, likes, and url for one or\n", pc.CYAN)
    pc.printout("more targets, with the possibility to specify dates for filtering the output\n", pc.CYAN)
    pc.printout("Type 'list' to show all allowed commands\n")
    pc.printout("-" * 80)


def cmdlist() -> None:
    pc.printout("credentials\t")
    pc.printout("Provide API Key\n", colour=pc.YELLOW)
    pc.printout("dates\t\t")
    pc.printout("Insert date or date range (dd/mm/yyyy format)\n", colour=pc.YELLOW)
    pc.printout("dshow\t\t")
    pc.printout("Show stored dates\n", colour=pc.YELLOW)
    pc.printout("run\t\t")
    pc.printout("When everything is set, the scraper will start running with this command\n", colour=pc.YELLOW)
    pc.printout("targets\t\t")
    pc.printout("Insert whitespace separated list of target(s), will overwrite old ones\n", colour=pc.YELLOW)
    pc.printout("tshow\t\t")
    pc.printout("Show comma separated list of target(s)\n", colour=pc.YELLOW)


def signal_handler(sig: object, frame: object) -> None:
    pc.printout("\nGoodbye!\n", pc.RED)
    sys.exit(0)


def completer(text: str, state: int) -> str or None:
    options = [i for i in commands if i.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None


def _quit() -> None:
    pc.printout("Goodbye!\n", pc.RED)
    sys.exit(0)


is_windows = False

welcome()

parser = argparse.ArgumentParser(description="Description")
parser.add_argument('targets', type=str, nargs='+',
                    help='target identificator, single or whitespace separated list')

parser.add_argument('-w', '--windows', action='store_true', default=False,
                    help='use this flag if your operating system is Windows, otherwise ignore it')

args = parser.parse_args()

try:
    import gnureadline
except:
    is_windows = args.windows
    import pyreadline

api = VkApiWrapper(args.targets)

commands = {
    'list': cmdlist,
    'help': cmdlist,
    'quit': _quit,
    'exit': _quit,
    'credentials': api.store_credentials,
    'dates': api.set_dates,
    'dshow': api.show_dates,
    'run': api.retrieve_targets_posts,
    'targets': api.set_targets,
    'tshow': api.show_targets
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
