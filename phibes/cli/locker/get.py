"""
Click interface to get Locker
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import get_config
from phibes.cli.lib import get_locker
from phibes.cli.lib import make_click_command


options = {
    '--verbose': click.option(
        '--verbose',
        help="Do you want a verbose report?",
        prompt="verbose", default=False, type=bool
    )
}

import copy
import pathlib
import getpass


def apply_options(options):
    def decorator(f):
        for option in reversed(options):
            option(f)
        return f
    return decorator


def get(config, locker, password, verbose):
    """

    """
    user_config = get_config(config)
    inst = get_locker(locker, password)
    if inst.lock_file.exists():
        click.echo(f"confirmed lock file {inst.lock_file} exists")
    if inst.path.exists():
        click.echo(f"confirmed locker dir {inst.path} exists")
    print(f"{inst} verbose: {verbose} todo")
    return inst


get_locker_cmd = make_click_command('get-locker', get, options)
