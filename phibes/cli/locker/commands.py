#!/usr/bin/env python
"""
Operation-centric command-line interface to phibes features
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.lib.locker import Locker


@click.group()
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.pass_context
def main_locker(ctx, locker, password):
    ctx.obj = {
        'locker': locker,
        'password': password,
    }


@main_locker.command()
@click.option('--locker', prompt='Locker')
@click.option(
    '--password',
    prompt='Password',
    hide_input=True,
    confirmation_prompt=True
)
def create_locker(locker, password):
    """
    Create a new locker
    :param locker: Name of locker to create
    :param password: Auth password for new locker
    :return:
    """
    new_locker = Locker(locker, password, create=True)
    click.echo(f"Locker created {locker}")
    click.echo(f"Locker created {new_locker.path}")
    return


@main_locker.command()
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
def delete_locker(locker, password):
    """
    Delete a locker
    :param locker: Name of locker to delete
    :param password: Auth password of locker
    :return:
    """
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
