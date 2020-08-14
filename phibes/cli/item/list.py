"""
Click interface to phibes items
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import catch_phibes_cli
from phibes.cli.lib import present_list_items
from phibes.lib.locker import registered_items


@click.command(name='list')
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to list',
    type=click.Choice(list(registered_items.keys()) + ['all']),
    default='all'
)
@click.option('--verbose', prompt='Verbose', default=False, type=bool)
@catch_phibes_cli
def list_items(locker, password, item_type, verbose):
    """
    Display the (unencrypted) names of all Secrets in the Locker
    :param locker:
    :param password:
    :param item_type:
    :param verbose:
    :return:
    """
    click.echo(
        present_list_items(locker, password, item_type, verbose)
    )
    return


@click.command()
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to list',
    type=click.Choice(list(registered_items.keys()) + ['all']),
    default='all'
)
@click.option('--verbose', prompt='Verbose', default=False, type=bool)
@catch_phibes_cli
def ls(locker, password, item_type, verbose):
    click.secho(
        present_list_items(locker, password, item_type, verbose),
        fg='green'
    )
    return
