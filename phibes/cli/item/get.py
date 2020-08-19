"""
Click interface to get an item
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import get_config
from phibes.cli.lib import make_click_command
from phibes.cli.lib import get_item as help_get_item
from phibes.lib.locker import registered_items


options = {
    'item_type': click.option(
        '--item_type',
        prompt='Type of item to get',
        help='Type of item to get',
        type=click.Choice(registered_items.keys()),
        default='secret'
    ),
    'item': click.option(
        '--item',
        prompt='Item name',
        help='Name of item to get',
    )
}


def get(config, locker, password, item_type, item):
    """
    Display the (unencrypted) contents of the named item_type:item
    :param locker:
    :param password:
    :param item_type:
    :param item:
    :return:
    """
    user_config = get_config(config)
    my_item = help_get_item(locker, password, item_type, item)
    click.echo(f"{my_item}")


get_item_cmd = make_click_command('get-item', get, options)
