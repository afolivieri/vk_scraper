#!/usr/bin/env python3


from src import printcolors as pc
from src.vk_scraper import VkScraper
from src.vk_downloader import VkDownloader
import argparse
import sys
import signal
from src.git_credentials import GitCredentialsHandler

is_windows = True

try:
    import gnureadline
except:
    is_windows = True
    from pyreadline3.rlmain import BaseReadline as PyRdl


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
    # API discarded, credentials not needed
    # pc.printout("credentials\t")
    # pc.printout("Provide API Key\n", colour=pc.YELLOW)
    pc.printout("dates\t\t")
    pc.printout("Insert date or date range (dd/mm/yyyy format)\n", colour=pc.YELLOW)
    pc.printout("download\t")
    pc.printout("Downloads media from link if they exist\n", colour=pc.YELLOW)
    pc.printout("dshow\t\t")
    pc.printout("Show stored dates\n", colour=pc.YELLOW)
    pc.printout("gitkey\t\t")
    pc.printout("Change GitHub Private Access Key\n", colour=pc.YELLOW)
    pc.printout("run\t\t")
    pc.printout("When everything is set, the scraper will start running with this command\n", colour=pc.YELLOW)
    pc.printout("targets\t\t")
    pc.printout("Insert whitespace separated list of target(s), will overwrite old ones\n", colour=pc.YELLOW)
    pc.printout("translate\t")
    pc.printout("After downloading targets walls you can translate it if in possession of DeepL API key\n", colour=pc.YELLOW)
    pc.printout("tshow\t\t")
    pc.printout("Show comma separated list of target(s)\n", colour=pc.YELLOW)
    pc.printout("update\t\t")
    pc.printout("Update translation credentials\n", colour=pc.YELLOW)


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


welcome()

parser = argparse.ArgumentParser(description="Description")
parser.add_argument('-t', '--targets', type=str, nargs='+',
                    help='target identificator, single or whitespace separated list')

args = parser.parse_args()

api_1 = VkScraper(args.targets)
api_2 = VkDownloader()
api_3 = GitCredentialsHandler()

commands = {
    'list': cmdlist,
    'help': cmdlist,
    'quit': _quit,
    'exit': _quit,
    # 'credentials': api.store_credentials, API discarded, credentials not needed
    'dates': api_1.set_dates,
    'download': api_2.download_media,
    'dshow': api_1.show_dates,
    'gitkey': api_3.set_github_key,
    'run': api_1.retrieve_targets_posts,
    'targets': api_1.set_targets,
    'translate': api_1.translating_target_csv,
    'tshow': api_1.show_targets,
    'update': api_1.update_credentials
}

signal.signal(signal.SIGINT, signal_handler)
if is_windows:
    PyRdl().parse_and_bind("tab: complete")
    PyRdl().set_completer(completer)
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
