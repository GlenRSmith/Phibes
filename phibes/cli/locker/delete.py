"""
Click interface to delete Locker
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import make_click_command
from phibes.cli.lib import PhibesNotFoundError
from phibes.lib.config import Config
from phibes.lib.locker import Locker


options = {}


def delete(config, locker, password):
    """
    Delete a locker
    """
    try:
        user_config = Config(config)
    except FileNotFoundError:
        raise PhibesNotFoundError(
            f"config file not found at {config}"
        )
    try:
        inst = Locker(locker, password)
    except FileNotFoundError:
        raise PhibesNotFoundError(
            f"locker {locker} not found"
        )
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


delete_locker_cmd = make_click_command('delete-locker', delete, options)
