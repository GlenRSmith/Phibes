"""
Click interface to delete Items
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import get_config
from phibes.cli.lib import delete_item as del_item
from phibes.cli.lib import make_click_command
from phibes.lib.locker import registered_items


options = {
    'item_type': click.option(
        '--item_type',
        prompt='Type of item to delete',
        type=click.Choice(registered_items.keys()),
        default='secret',
        help='the type of item to delete - default is `secret`'
    ),
    'item': click.option(
        '--item',
        prompt='Item name',
        type=str,
        help='The name of the item to delete'
    )
}


def delete(config, locker, password, item_type, item):
    """
    Remove the named Item from the Locker
    :param config:
    :param locker:
    :param password:
    :param item_type:
    :param item:
    :return:
    """
    user_config = get_config(config)
    del_item(locker, password, item_type, item)


delete_item_cmd = make_click_command('delete-item', delete, options)
