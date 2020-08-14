"""
Click interface to phibes items
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import catch_phibes_cli
from phibes.cli.lib import delete_item as del_item
from phibes.lib.locker import registered_items


@click.command(name='delete')
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to delete',
    type=click.Choice(registered_items.keys()),
    default='secret'
)
@click.option('--item', prompt='Item name')
@catch_phibes_cli
def delete_item(locker, password, item_type, item):
    """
    Remove the named Item from the Locker
    :param locker:
    :param password:
    :param item_type:
    :param item:
    :return:
    """
    del_item(locker, password, item_type, item)
