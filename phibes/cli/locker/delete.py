"""
Click interface to create Locker
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import PhibesNotFoundError
from phibes.lib.config import Config
from phibes.lib.locker import Locker


@click.command(name='delete-locker')
@click.pass_context
def delete_locker(ctx):
    """
    Delete a locker
    :param ctx: click context object
    :return:
    """
    config = ctx.obj['config']
    try:
        user_config = Config(config)
    except FileNotFoundError:
        raise PhibesNotFoundError(
            f"config file not found at {config}"
        )
    locker = ctx.obj['locker']
    password = ctx.obj['password']
    inst = Locker(locker, password)
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
