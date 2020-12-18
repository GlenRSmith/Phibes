"""
Click interface to phibes items
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.command_base import ConfigFileLoadingCmd
from phibes.cli.lib import get_locker
from phibes.cli.lib import present_list_items
from phibes.cli.options import verbose_item_option


class ListItemsCmd(ConfigFileLoadingCmd):
    """
    Command to list items in a locker
    """

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
        locker_inst = get_locker(
            locker_name=locker, password=password
        )
        click.echo(present_list_items(locker_inst, verbose))


options = {'verbose': verbose_item_option}
list_items_cmd = ListItemsCmd.make_click_command('list', options)
