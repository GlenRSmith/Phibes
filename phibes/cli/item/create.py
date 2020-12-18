"""
Click command for `create-item`
"""

# core library modules

# third party packages

# in-project modules
from phibes.cli.command_base import ConfigFileLoadingCmd
from phibes.cli.lib import create_item
from phibes.cli.options import item_name_option, template_name_option


class CreateItemCmd(ConfigFileLoadingCmd):
    """
    Command to create a new item in a locker
    """

    def __init__(self):
        super(CreateItemCmd, self).__init__()
        return

    @staticmethod
    def handle(
            config,
            locker,
            password,
            item,
            template,
            *args, **kwargs
    ):
        """
        Launch editor to create/update an item in a locker

        :param config:
        :param locker:
        :param password:
        :param item:
        :param template:
        :return:
        """
        super(CreateItemCmd, CreateItemCmd).handle(
            config, *args, **kwargs
        )
        if template == 'Empty':
            template = None
        return create_item(locker, password, item, template)


options = {
    'item': item_name_option,
    'template': template_name_option
}


create_item_cmd = CreateItemCmd.make_click_command('create-item', options)
