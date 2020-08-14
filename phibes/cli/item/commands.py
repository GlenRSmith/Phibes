"""
Click interface to phibes items
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli_lib import present_list_items
from phibes.cli_lib import PhibesCliError, PhibesExistsError
from phibes.cli_lib import PhibesNotFoundError
from phibes.lib.config import Config
from phibes.lib.item import Item
from phibes.lib.locker import Locker, registered_items


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
    prompt='Type of item to list',
    type=click.Choice(list(registered_items.keys()) + ['all']),
    default='all'
)
@click.option('--verbose', prompt='Verbose', default=False, type=bool)
def ls(locker, password, item_type, verbose):
    # verbose = make_str_bool(verbose)
    click.secho(
        present_list_items(locker, password, item_type, verbose),
        fg='green'
    )
    return
