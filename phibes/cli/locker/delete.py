"""
Click interface to delete Locker
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import get_config
from phibes.cli.lib import get_locker
from phibes.cli.lib import make_click_command
from phibes.lib.locker import Locker


options = {}


def delete(config, locker, password):
    """
    Delete a locker
    """
    user_config = get_config(config)
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


delete_locker_cmd = make_click_command('delete-locker', delete, options)
