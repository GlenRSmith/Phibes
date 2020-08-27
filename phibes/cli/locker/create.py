"""
Click interface to create Locker
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.command_base import ConfigFileLoadingCmd
from phibes.lib.errors import PhibesExistsError
from phibes.cli.lib import PhibesCliExistsError
from phibes.lib.locker import Locker


class CreateLockerCmd(ConfigFileLoadingCmd):

    def __init__(self):
        super(CreateLockerCmd, self).__init__()
        return

    @staticmethod
    def handle(config, locker, password, *args, **kwargs):
        super(CreateLockerCmd, CreateLockerCmd).handle(
            config, *args, **kwargs
        )
        try:
            new_locker = Locker(locker, password, create=True)
        except PhibesExistsError as err:
            raise PhibesCliExistsError(
                f"Locker {locker} already exists\n{err}"
            )
        click.echo(f"Locker created {locker}")
        click.echo(f"Locker created {new_locker.path}")
        return


options = {
    'password': click.option(
        '--password',
        prompt='Locker Password',
        hide_input=True,
        confirmation_prompt=True
    )
}


create_locker_cmd = CreateLockerCmd.make_click_command(
    'create-locker', options
)
