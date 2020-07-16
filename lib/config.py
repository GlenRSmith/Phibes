"""
Package configuration
"""

# Built-in library packages
import os
from pathlib import Path
import sys

# Third party packages
from colorama import init as color_init
from colorama import Fore, Style

# In-project modules
# Do not do that here. This is a 'leaf' module.

LOCKER_PATH = "locker"
USER_EDIT_PATH = os.path.join(LOCKER_PATH, 'tmp')
USER_EDIT_FILE = os.path.join(USER_EDIT_PATH, 'tmp.txt')
EDITOR = ''


def init_config(self):
    """ Initializes the config (will wipe-out anything there)"""
    color_init()
    print(f"{Style.RESET_ALL}{Style.BRIGHT}Initial configuration")
    print(f"{Style.RESET_ALL}Please enter your desired settings,")
    print("defaults are in square brackets\n")
    print(f"{Style.BRIGHT}{Fore.GREEN} + Directory:")
    conf_dir = Path.home().joinpath('.ppp')
    user_path = f"{Style.RESET_ALL}[{Style.DIM}{conf_dir}{Style.RESET_ALL}]"
    if user_path == '':
        user_path = conf_dir
    print(f"\n{Style.BRIGHT}{Style.GREEN}Editor, blank for env $EDITOR:")
    editor = input(f"{Style.RESET_ALL}[] ")
    self.cfg['ppp'] = {}
    self.cfg['ppp']['editor'] = editor
    with open(self.torgo_cfg, 'w') as f:
        self.cfg.write(f)


def get_user_editor():
    global EDITOR
    if EDITOR == '':
        if 'EDITOR' in os.environ:
            EDITOR = os.environ['EDITOR']
        else:
            print(
                Style.RESET_ALL
                + Style.BRIGHT
                + Fore.RED
                + "ERROR, NO EDITOR FOUND!\n"
                + Style.RESET_ALL
            )
            print("Please set an editor.")
            sys.exit(1)
    return EDITOR
