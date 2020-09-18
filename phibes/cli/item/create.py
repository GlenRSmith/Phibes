"""
Click command for `edit`
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.command_base import ConfigFileLoadingCmd
from phibes.cli.lib import create_item
from phibes.model.locker import registered_items


class CreateItemCmd(ConfigFileLoadingCmd):

    def __init__(self):
        super(CreateItemCmd, self).__init__()
        return

    @staticmethod
    def handle(
            config,
            locker,
            password,
            item_type,
            item,
            template,
            *args, **kwargs
    ):
        """
        Launch editor to create/update an item in a locker

        :param config:
        :param locker:
        :param password:
        :param item_type:
        :param item:
        :param template:
        :return:
        """
        super(CreateItemCmd, CreateItemCmd).handle(
            config, *args, **kwargs
        )
        if template == 'Empty':
            template = None
        return create_item(
            locker, password, item_type, item, template
        )


options = {
    'item_type': click.option(
        '--item_type',
        prompt='Type of item to edit',
        help='Type of item to edit',
        type=click.Choice(registered_items.keys()),
        default='secret'
    ),
    'item': click.option(
        '--item',
        prompt='Item name',
        help='Name of item to edit',
    ),
    'template': click.option(
        '--template',
        prompt='Name of item to start with',
        help='Name of item to start with',
        default='Empty'
    )
}


create_item_cmd = CreateItemCmd.make_click_command('create-item', options)
