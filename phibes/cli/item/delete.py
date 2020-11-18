"""
Click interface to delete Items
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.command_base import ConfigFileLoadingCmd
from phibes.cli.lib import delete_item as del_item


class DeleteItemCmd(ConfigFileLoadingCmd):

    def __init__(self):
        super(DeleteItemCmd, self).__init__()
        return

    @staticmethod
    def handle(config, locker, password, item, *args, **kwargs):
        """
        Remove the named Item from the Locker
        :param config:
        :param locker:
        :param password:
        :param item:
        :return:
        """
        super(DeleteItemCmd, DeleteItemCmd).handle(
            config, *args, **kwargs
        )
        del_item(locker, password, item)


options = {
    'item': click.option(
        '--item',
        prompt='Item name',
        type=str,
        help='The name of the item to delete'
    )
}


delete_item_cmd = DeleteItemCmd.make_click_command('delete-item', options)
