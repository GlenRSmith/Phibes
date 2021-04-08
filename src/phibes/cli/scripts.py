"""
Click-based command-line interface to phibes

Two entry points are implemented; setup makes them available on command-line
"""
# core library modules
from os import getcwd

# third party packages
# in-project modules
from phibes.cli.commands import build_cli_app
from phibes.cli.commands import ANON_COMMAND_DICT, NAMED_COMMAND_DICT
from phibes.cli.cli_config import CliConfig
from phibes.cli.lib import main, main_func


def anon_lockers():
    conf = CliConfig()
    conf.store_path = getcwd()
    build_cli_app(
        command_dict=ANON_COMMAND_DICT, click_group=main, named_locker=False
    )
    main_func()


def named_lockers():
    build_cli_app(
        command_dict=NAMED_COMMAND_DICT, click_group=main, named_locker=True
    )
    main_func()
