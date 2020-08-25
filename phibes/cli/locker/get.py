"""
Click interface to get Locker
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.command_base import ConfigFileLoadingCmd
from phibes.cli.lib import get_locker


class GetLockerCmd(ConfigFileLoadingCmd):

    def __init__(self):
        super(GetLockerCmd, self).__init__()
        return

    @staticmethod
    def handle(config, locker, password, verbose, *args, **kwargs):
        super(GetLockerCmd, GetLockerCmd).handle(
            config, *args, **kwargs
        )
        inst = get_locker(locker, password)
        if inst.lock_file.exists():
            click.echo(f"confirmed lock file {inst.lock_file} exists")
        if inst.path.exists():
            click.echo(f"confirmed locker dir {inst.path} exists")
        print(f"{inst} verbose: {verbose} todo")
        return inst


options = {
    'verbose': click.option(
        '--verbose',
        help="Do you want a verbose report?",
        prompt="verbose", default=False, type=bool
    )
}

get_locker_cmd = GetLockerCmd.make_click_command(
    'get-locker', options, exclude_common=False
)
