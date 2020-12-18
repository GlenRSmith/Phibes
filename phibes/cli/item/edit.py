"""
Click command for `edit`
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.command_base import ConfigFileLoadingCmd
from phibes.cli.lib import edit_item
from phibes.cli.options import item_name_option


class EditItemCmd(ConfigFileLoadingCmd):

    def __init__(self):
        super(EditItemCmd, self).__init__()
        return

    @staticmethod
    def handle(
            config,
            locker,
            password,
            item,
            *args, **kwargs
    ):
        """
        Launch editor to create/update an item in a locker

        :param config:
        :param locker:
        :param password:
        :param item:
        :return:
        """
        super(EditItemCmd, EditItemCmd).handle(
            config, *args, **kwargs
        )
        return edit_item(locker, password, item)


options = {'item': item_name_option}
edit_item_cmd = EditItemCmd.make_click_command('edit', options)
