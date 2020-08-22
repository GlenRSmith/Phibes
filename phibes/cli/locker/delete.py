"""
Click interface to delete Locker
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.command_base import ConfigFileLoadingCmd
from phibes.cli.lib import get_locker
from phibes.cli.lib import make_click_command
from phibes.lib.locker import Locker


class DeleteLockerCmd(ConfigFileLoadingCmd):

    def __init__(self):
        super(DeleteLockerCmd, self).__init__()
        return

    @staticmethod
    def handle(config, locker, password, *args, **kwargs):
        super(DeleteLockerCmd, DeleteLockerCmd).handle(
            config, *args, **kwargs
        )
        inst = get_locker(locker, password)
        if inst.lock_file.exists():
            click.echo(f"confirmed lock file {inst.lock_file} exists")
        if inst.path.exists():
            click.echo(f"confirmed locker dir {inst.path} exists")
        Locker.delete(locker, password)
        if not inst.lock_file.exists():
            click.echo(f"confirmed lock file {inst.lock_file} removed")
        else:
            click.echo(f"lock file {inst.lock_file} not removed")
        if not inst.path.exists():
            click.echo(f"confirmed locker dir {inst.path} removed")
        else:
            click.echo(f"locker dir {inst.path} not removed")
        click.echo(f"Locker deleted {locker}")
        return


options = {}


delete_locker_cmd = DeleteLockerCmd.make_click_command(
    'delete-locker', options
)
