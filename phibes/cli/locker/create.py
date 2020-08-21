"""
Click interface to create Locker
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import make_click_command
from phibes.cli.lib import PhibesExistsError
from phibes.lib.config import load_config
from phibes.lib.locker import Locker


options = {
    'password': click.option(
        '--password',
        prompt='Locker Password',
        hide_input=True,
        confirmation_prompt=True
    )
}


def create(config, locker, password):
    """
    Create a new Locker
    """
    # import pdb
    # pdb.set_trace()
    load_config(config)
    try:
        new_locker = Locker(locker, password, create=True)
    except FileExistsError as err:
        raise PhibesExistsError(
            f"Locker {locker} already exists\n{err}"
        )
    click.echo(f"Locker created {locker}")
    click.echo(f"Locker created {new_locker.path}")
    return


create_locker_cmd = make_click_command('create-locker', create, options)
