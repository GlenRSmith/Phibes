"""
Click interface to phibes items
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.command_base import ConfigFileLoadingCmd
from phibes.cli.lib import present_list_items


class ListItemsCmd(ConfigFileLoadingCmd):

    def __init__(self):
        super(ListItemsCmd, self).__init__()
        return

    @staticmethod
    def handle(
            config, locker, password, verbose, *args, **kwargs
    ):
        """
        Display the (unencrypted) names of all matching Items in the Locker
        :param config:
        :param locker:
        :param password:
        :param verbose: Include unencrypted item content in the report
        :return:
        """
        super(ListItemsCmd, ListItemsCmd).handle(
            config, *args, **kwargs
        )
        click.echo(
            present_list_items(locker, password, verbose)
        )


options = {
    'verbose': click.option(
        '--verbose',
        prompt='Verbose',
        help='Present entire contents of each item',
        default=False,
        type=bool
    )
}


list_items_cmd = ListItemsCmd.make_click_command('list', options)
