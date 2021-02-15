"""
Click interface to create Locker
"""

# core library modules
# third party packages
import click

# in-project modules
from phibes.cli.command_base import PhibesCommandBareBase
from phibes.cli.command_base import config_option
from phibes.cli.errors import PhibesCliError, PhibesCliExistsError
from phibes.cli.options import crypt_choices, crypt_option
from phibes.cli.options import locker_name_option
from phibes.cli.options import locker_path_option
from phibes.cli.options import new_password_option
from phibes.lib.config import ConfigModel, load_config_file
from phibes.lib.errors import PhibesExistsError
from phibes.model import Locker


class CreateLockerCmd(PhibesCommandBareBase):
    """
    Class to create and run click command to create a locker
    """

    options = {
        'config': config_option,
        'path': locker_path_option,
        'password': new_password_option,
        'crypt_id': crypt_option,
    }

    def __init__(self):
        super(CreateLockerCmd, self).__init__()

    @staticmethod
    def handle(*args, **kwargs):
        """Create a new Locker"""
        # parent class sets up environment variables from args
        super(CreateLockerCmd, CreateLockerCmd).handle(*args, **kwargs)
        try:
            password = kwargs.pop('password')
            crypt_int = kwargs.pop('crypt_id')
            crypt_id = crypt_choices.choice_dict[crypt_int]
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
        pth = storage_path.resolve()
        if locker:
            pth = pth / Locker.get_stored_name(locker)
        click.confirm(
            (
                f"Will attempt to create locker at\n"
                f"{pth}\n{crypt_id=}\n"
                f"Enter `y` to accept, `N` to abort"
            ), abort=True
        )
        try:
            new_locker = Locker.create(
                password=password,
                crypt_id=crypt_id,
                name=locker,
                path=storage_path
            )
        except PhibesExistsError as err:
            raise PhibesCliExistsError(
                f"Locker {locker} already exists\n{err}"
            )
        # TODO: use Locker.status!
        click.echo(f"Locker created {new_locker.path.resolve()}")
        if locker:
            click.echo(f"with name {locker}")


class CreateNamedLockerCmd(CreateLockerCmd):
    """
    Class to create and run click command to create a named locker
    """

    options = {
        'config': config_option,
        'locker': locker_name_option,
        'password': new_password_option,
        'crypt_id': crypt_option,
    }

    def __init__(self):
        super(CreateNamedLockerCmd, self).__init__()
