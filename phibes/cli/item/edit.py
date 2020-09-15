"""
Click command for `edit`
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.command_base import ConfigFileLoadingCmd
from phibes.cli.lib import edit_item
from phibes.model.locker import registered_items


class EditItemCmd(ConfigFileLoadingCmd):

    def __init__(self):
        super(EditItemCmd, self).__init__()
        return

    @staticmethod
    def handle(
            config,
            locker,
            password,
            item_type,
            item,
            overwrite,
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
        :param overwrite:
        :param template:
        :return:
        """
        super(EditItemCmd, EditItemCmd).handle(
            config, *args, **kwargs
        )
        if template == 'Empty':
            template = None
        return edit_item(
            locker, password, item_type, item, overwrite, template
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
    'overwrite': click.option(
        '--overwrite',
        type=bool,
        prompt='Should any existing item be overwritten?',
        help='Whether to overwrite existing item',
        default=False
    ),
    'template': click.option(
        '--template',
        prompt='Name of template to start with',
        help='Name of template to start with',
        default='Empty'
    )
}


edit_item_cmd = EditItemCmd.make_click_command('edit', options)
