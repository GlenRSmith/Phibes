"""
Click interface to delete Locker
"""
# core library modules
# third party packages
import click

# in-project modules
from phibes.cli.command_base import PhibesCommand
from phibes.cli.command_base import config_option
from phibes.cli.lib import get_locker_args
from phibes.cli.options import locker_name_option
from phibes.cli.options import locker_path_option
from phibes.cli.options import password_option


class DeleteLockerCmd(PhibesCommand):
    """
    Class to create and run click command to delete a locker
    """

    options = {
        'config': config_option,
        'path': locker_path_option,
        'password': password_option
    }

    def __init__(self):
        super(DeleteLockerCmd, self).__init__()

    @staticmethod
    def handle(*args, **kwargs):
        """Delete a Locker"""
        super(DeleteLockerCmd, DeleteLockerCmd).handle(*args, **kwargs)
        locker = kwargs.get('locker', None)
        inst = get_locker_args(*args, **kwargs)
        click.confirm(
            (
                f"Will attempt to delete locker with\n"
                f"{inst.path.resolve()}\n"
                f"Enter `y` to accept, `N` to abort"
            ), abort=True
        )
        if inst.lock_file.exists():
            click.echo(f"confirmed lock file {inst.lock_file} exists")
        if inst.path.exists():
            click.echo(f"confirmed locker dir {inst.path} exists")
        inst.delete_instance(name=locker)
        if not inst.lock_file.exists():
            click.echo(f"confirmed lock file {inst.lock_file} removed")
        else:
            click.echo(f"lock file {inst.lock_file} not removed")
        if not inst.path.exists():
            click.echo(f"confirmed locker dir {inst.path} removed")
        else:
            click.echo(f"locker dir {inst.path} not removed")
        click.echo(f"Locker deleted from {inst.path}")


class DeleteNamedLockerCmd(DeleteLockerCmd):
    """
    Class to create and run click command to delete a named locker
    """

    options = {
        'config': config_option,
        'locker': locker_name_option,
        'password': password_option
    }

    def __init__(self):
        super(DeleteNamedLockerCmd, self).__init__()
