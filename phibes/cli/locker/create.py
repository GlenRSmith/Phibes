"""
Click interface to create Locker
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.command_base import PhibesCommandBareBase
from phibes.cli.command_base import config_option
from phibes.cli.lib import PhibesCliExistsError
from phibes.cli.options import crypt_choices, crypt_option
from phibes.cli.options import locker_name_option
from phibes.cli.options import new_password_option
from phibes.lib.errors import PhibesExistsError
from phibes.model import Locker


class CreateLockerCmd(PhibesCommandBareBase):
    """
    Class to create and run click command to create a locker
    """

    options = {
        'config': config_option,
        'locker': locker_name_option,
        'password': new_password_option,
        'crypt_id': crypt_option,
    }

    def __init__(self):
        super(CreateLockerCmd, self).__init__()

    @staticmethod
    def handle(config, locker, password, crypt_id, *args, **kwargs):
        """
        Handler for the command
        """
        super(CreateLockerCmd, CreateLockerCmd).handle(
            config, *args, **kwargs
        )
        try:
            new_locker = Locker.create(
                name=locker,
                password=password,
                crypt_id=crypt_choices.choice_dict[crypt_id]
            )
        except PhibesExistsError as err:
            raise PhibesCliExistsError(
                f"Locker {locker} already exists\n{err}"
            )
        click.echo(f"Locker created {locker}")
        click.echo(f"Locker created {new_locker.path}")


create_locker_cmd = CreateLockerCmd.make_click_command('create-locker')
