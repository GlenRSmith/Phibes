"""
Click interface to delete Locker
"""

# core library modules
# third party packages
import click

# in-project modules
from phibes.cli.command_base import PhibesCommandBareBase
from phibes.cli.command_base import config_option
from phibes.cli.errors import PhibesCliError
from phibes.cli.options import locker_name_option
from phibes.cli.options import locker_path_option
from phibes.cli.options import password_option
from phibes.lib.config import ConfigModel, load_config_file
from phibes.model import Locker


class DeleteLockerCmd(PhibesCommandBareBase):
    """
    Class to create and run click command to create a locker
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
        # parent class sets up environment variables from args
        super(DeleteLockerCmd, DeleteLockerCmd).handle(*args, **kwargs)
        try:
            password = kwargs.pop('password')
        except KeyError as err:
            raise PhibesCliError(f'missing required param {err}')
        if 'path' in kwargs:
            storage_path = kwargs.pop('path')
        elif 'config' in kwargs:
            config = kwargs.pop('config')
            load_config_file(config)
            storage_path = ConfigModel().store_path
        else:
            raise PhibesCliError(
                f'path param must be provided by param or in config file'
            )
        # locker name is optional, only settable from command-line
        locker = kwargs.pop('locker', None)
        inst = Locker.get(
            password=password, name=locker, path=storage_path
        )
        click.confirm(
            (
                f"Will attempt to delete locker with\n"
                f"{storage_path.resolve()}\n"
                f"Enter `y` to accept, `N` to abort"
            ), abort=True
        )
        if inst.lock_file.exists():
            click.echo(f"confirmed lock file {inst.lock_file} exists")
        if inst.path.exists():
            click.echo(f"confirmed locker dir {inst.path} exists")
        Locker.delete(password=password, name=locker, path=storage_path)
        if not inst.lock_file.exists():
            click.echo(f"confirmed lock file {inst.lock_file} removed")
        else:
            click.echo(f"lock file {inst.lock_file} not removed")
        if not inst.path.exists():
            click.echo(f"confirmed locker dir {inst.path} removed")
        else:
            click.echo(f"locker dir {inst.path} not removed")
        click.echo(f"Locker deleted from {storage_path}")


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
