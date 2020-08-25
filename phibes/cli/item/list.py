"""
Click interface to phibes items
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import make_click_command
from phibes.cli.lib import present_list_items
from phibes.lib.config import load_config_file
from phibes.lib.locker import registered_items


options = {
    'item-type': click.option(
        '--item_type',
        prompt='Type of item to list',
        help='Type of item to list - default `all`',
        type=click.Choice(list(registered_items.keys()) + ['all']),
        default='all'
    ),
    'verbose': click.option(
        '--verbose',
        prompt='Verbose',
        help='Present entire contents of each item',
        default=False,
        type=bool
    )
}


def list_items(config, locker, password, item_type, verbose):
    """
    Display the (unencrypted) names of all Secrets in the Locker
    :param config:
    :param locker:
    :param password:
    :param item_type:
    :param verbose:
    :return:
    """
    load_config_file(config)
    click.echo(
        present_list_items(locker, password, item_type, verbose)
    )
    return


list_items_cmd = make_click_command('list', list_items, options)
