"""
Click command for `edit`
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import get_config
from phibes.cli.lib import make_click_command
from phibes.cli.lib import edit_item
from phibes.lib.config import Config
from phibes.lib.locker import registered_items


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
    ),
    'editor': click.option(
        '--editor',
        prompt='Editor',
        help='Editor to use (Phibes will attempt to launch)',
        default=Config('.').editor
    )
}


def edit(
        config, locker, password, item_type, item, editor, overwrite, template
):
    """
    Launch editor to create/update an item in a locker

    :param config:
    :param locker:
    :param password:
    :param item_type:
    :param item:
    :param editor:
    :param overwrite:
    :param template:
    :return:
    """
    user_config = get_config(config)
    if template == 'Empty':
        template = None
    return edit_item(
        locker, password, item_type, item, overwrite, template, editor
    )


edit_item_cmd = make_click_command('edit', edit, options)