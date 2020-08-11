"""
Click interface to phibes items
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli_lib import edit_item, present_list_items
from phibes.cli_lib import make_str_bool
from phibes.lib.config import Config
from phibes.lib.item import Item
from phibes.lib.locker import Locker, registered_items


@click.command()
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to list',
    type=click.Choice(list(registered_items.keys()) + ['all']),
    default='all'
)
@click.option('--verbose', prompt='Verbose', default=False)
def ls(locker, password, item_type, verbose):
    verbose = make_str_bool(verbose)
    click.secho(
        present_list_items(
            locker, password, item_type, verbose
        ),
        fg='green'
    )
    return


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
def edit(
        locker, password, item_type, item, editor, overwrite, template
):
    if template == 'Empty':
        template = None
    return edit_item(
        locker, password, item_type, item, overwrite, template, editor
    )


@click.command()
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to show',
    type=click.Choice(registered_items.keys()),
    default='secret'
)
@click.option('--item', prompt='Item name')
def show_item(locker, password, item_type, item):
    """
    Display the (unencrypted) contents of the named Secret
    :param locker:
    :param password:
    :param item_type:
    :param item:
    :return:
    """
    my_locker = Locker.find(locker, password)
    my_item = Item.find(my_locker, item, item_type)
    if not my_item:
        click.echo(f"Item {item} does not exist")
    click.echo(f"{my_item}")


@click.command()
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to delete',
    type=click.Choice(registered_items.keys()),
    default='secret'
)
@click.option('--item', prompt='Item name')
def delete_item(locker, password, item_type, item):
    """
    Remove the named Item from the Locker
    :param locker:
    :param password:
    :param item_type:
    :param item:
    :return:
    """
    my_locker = Locker.find(locker, password)
    my_item = Item.find(my_locker, item, item_type)
    if not my_item:
        click.echo(f"Item {item} does not exist")
    else:
        Item.delete(my_locker, item, item_type)
    click.echo(f"{my_item}")


@click.command()
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to list',
    type=click.Choice(list(registered_items.keys()) + ['all']),
    default='all'
)
@click.option('--verbose', prompt='Verbose', default=False)
def list_items(locker, password, item_type, verbose):
    """
    Display the (unencrypted) names of all Secrets in the Locker
    :param locker:
    :param password:
    :param item_type:
    :param verbose:
    :return:
    """
    verbose = make_str_bool(verbose)
    click.echo(
        present_list_items(locker, password, item_type, verbose)
    )
    return
