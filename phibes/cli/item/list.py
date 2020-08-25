"""
Click interface to phibes items
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.command_base import ConfigFileLoadingCmd
from phibes.cli.lib import present_list_items
from phibes.lib.locker import registered_items


class ListItemsCmd(ConfigFileLoadingCmd):

    def __init__(self):
        super(ListItemsCmd, self).__init__()
        return

    @staticmethod
    def handle(
            config, locker, password, item_type, verbose, *args, **kwargs
    ):
        """
        Display the (unencrypted) names of all matching Items in the Locker
        :param config:
        :param locker:
        :param password:
        :param item_type: Optional filter on type of item to display
        :param verbose: Include unencrypted item content in the report
        :return:
        """
        super(ListItemsCmd, ListItemsCmd).handle(
            config, *args, **kwargs
        )
        click.echo(
            present_list_items(locker, password, item_type, verbose)
        )


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


list_items_cmd = ListItemsCmd.make_click_command('list', options)
