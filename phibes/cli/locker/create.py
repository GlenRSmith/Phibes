"""
Click interface to create Locker
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import catch_phibes_cli
from phibes.cli.lib import PhibesNotFoundError, PhibesPasswordError
from phibes.lib.config import Config
from phibes.lib.locker import Locker
from secrets import compare_digest


@click.command(name='create-locker')
@click.pass_context
@click.option('--password_conf', prompt='Confirm password', hide_input=True)
@catch_phibes_cli
def create_locker(ctx, password_conf):
    """
    Create a new locker
    :param ctx: click context object
    :param password_conf: confirmation password
    :return:
    """
    config = ctx.obj['config']
    locker = ctx.obj['locker']
    password = ctx.obj['password']
    if not compare_digest(password_conf, password):
        raise PhibesPasswordError('Passwords do not match')
    try:
        user_config = Config(config)
    except FileNotFoundError:
        raise PhibesNotFoundError(
            f"config file not found at {config}"
        )
    new_locker = Locker(locker, password, create=True)
    click.echo(f"Locker created {locker}")
    click.echo(f"Locker created {new_locker.path}")
    return
