"""
Click command for `edit`
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import catch_phibes_cli
from phibes.cli.lib import edit_item
from phibes.lib.config import Config
from phibes.lib.locker import registered_items


@click.command()
@click.option('--locker', prompt='Locker name')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to edit',
    type=click.Choice(registered_items.keys()),
    default='secret'
)
@click.option('--item', prompt='Item name')
@click.option(
    '--overwrite',
    prompt='Should any existing item be overwritten?',
    default=False
)
@click.option(
    '--template',
    prompt='Name of template to start with',
    default='Empty'
)
@click.option(
    '--editor',
    prompt='Editor',
    default=Config('.').editor
)
@catch_phibes_cli
def edit(
        locker, password, item_type, item, editor, overwrite, template
):
    """
    Use your text editor to create or update an item in your locker
    :param locker:
    :param password:
    :param item_type:
    :param item:
    :param editor:
    :param overwrite:
    :param template:
    :return:
    """
    if template == 'Empty':
        template = None
    return edit_item(
        locker, password, item_type, item, overwrite, template, editor
    )
