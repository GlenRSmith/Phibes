"""
Click interface to phibes items
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import catch_phibes_cli
from phibes.cli.lib import get_item as help_get_item
from phibes.lib.locker import registered_items


@click.command(name='get')
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to get',
    type=click.Choice(registered_items.keys()),
    default='secret'
)
@click.option('--item', prompt='Item name')
@catch_phibes_cli
def get_item(locker, password, item_type, item):
    """
    Display the (unencrypted) contents of the named item_type:item
    :param locker:
    :param password:
    :param item_type:
    :param item:
    :return:
    """
    my_item = help_get_item(locker, password, item_type, item)
    click.echo(f"{my_item}")
