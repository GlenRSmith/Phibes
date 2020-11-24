"""
Click interface to get an item
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.command_base import ConfigFileLoadingCmd
from phibes.cli.lib import get_item as help_get_item


class GetItemCmd(ConfigFileLoadingCmd):

    def __init__(self):
        super(GetItemCmd, self).__init__()
        return

    @staticmethod
    def handle(config, locker, password, item, *args, **kwargs):
        """
        Get the named Item from the Locker
        :param config:
        :param locker:
        :param password:
        :param item:
        :return:
        """
        super(GetItemCmd, GetItemCmd).handle(
            config, *args, **kwargs
        )
        my_item = help_get_item(locker, password, item)
        click.echo(f"{my_item}")


options = {
    'item': click.option(
        '--item',
        prompt='Item name',
        help='Name of item to get',
    )
}


get_item_cmd = GetItemCmd.make_click_command('get-item', options)
