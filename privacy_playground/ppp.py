#!/usr/bin/env python
"""
Operation-centric command-line interface to python privacy playground features
"""

# core library modules

# third party packages
import click

# in-project modules
from privacy_playground.cli_lib import edit_item, present_list_items
from privacy_playground.cli_lib import make_str_bool
from privacy_playground.lib.config import Config
from privacy_playground.lib.item import Item
from privacy_playground.lib.locker import Locker


@click.group()
def main():
    pass


@main.command()
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to list',
    type=click.Choice(Item.get_item_types() + ['all']),
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


@main.command()
@click.option('--locker', prompt='Name of Locker')
@click.option(
    '--password', prompt='New Locker password', hide_input=True,
    confirmation_prompt=True
)
def create_locker(locker, password):
    """
    Create a new locker
    :param locker: Name of locker to create
    :param password: Password of locker to create
    :return:
    """
    new_locker = Locker(locker, password, create=True)
    click.echo(f"Locker created {locker}")
    click.echo(f"Locker created {new_locker.path}")
    return


@main.command()
@click.option('--locker', prompt='Locker Name')
@click.option('--password', prompt='Locker password', hide_input=True,)
def delete_locker(locker, password):
    inst = Locker(locker, password)
    if inst.lock_file.exists():
        click.echo(f"confirmed lock file {inst.lock_file} exists")
    if inst.path.exists():
        click.echo(f"confirmed locker dir {inst.path} exists")
    Locker.delete(locker, password)
    if not inst.lock_file.exists():
        click.echo(f"confirmed lock file {inst.lock_file} removed")
    else:
        click.echo(f"lock file {inst.lock_file} not removed")
    if not inst.path.exists():
        click.echo(f"confirmed locker dir {inst.path} removed")
    else:
        click.echo(f"locker dir {inst.path} not removed")
    click.echo(f"Locker deleted {locker}")
    return


@main.command()
@click.option('--locker', prompt='Locker name')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to edit',
    type=click.Choice(Item.get_item_types()),
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


@main.command()
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to show',
    type=click.Choice(Item.get_item_types()),
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


@main.command()
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to delete',
    type=click.Choice(Item.get_item_types()),
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


@main.command()
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to list',
    type=click.Choice(Item.get_item_types() + ['all']),
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


if __name__ == '__main__':
    main()
