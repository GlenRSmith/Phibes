#!/usr/bin/env python
"""
Operation-centric command-line interface to python privacy playground features
"""

# core library modules

# third party packages
import click

# for purposes of the CLI project, lib is being treated as third-party!
from cli_lib import edit_item
from lib.config import Config
from lib.item import Item
from lib.locker import Locker


@click.group()
def main():
    pass


@main.group()
def util():
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
def ls(locker, password, item_type):
    if item_type == 'all':
        item_type = None
    my_locker = Locker.find(locker, password)
    items = Item.find_all(my_locker, item_type)
    longest = 10
    for sec in items:
        longest = (longest, len(sec.name))[longest < len(sec.name)]
    print(f"{'Item Type':>15}{'Item Name':>{longest+2}}")
    for sec in items:
        print(
            f"{str(sec.item_type).rjust(4, '-'):>15}"
            f"{str(sec.name):>{longest+2}}"
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
    new_locker = Locker.create_and_save(locker, password)
    click.echo(f"Locker created {new_locker.path}")
    return


@main.command()
def no():
    """
    """
    import os, tempfile
    from pathlib import Path
    tmpdir = tempfile.mkdtemp(dir=Path.cwd().absolute())
    click.echo(f"{tmpdir}")
    os.chdir(tmpdir)
    return


@main.command()
@click.option('--locker', prompt='Locker Name')
@click.option('--password', prompt='Locker password', hide_input=True,)
def delete_locker(locker, password):
    inst = Locker(locker)
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
@click.option('--editor', prompt='Editor', default=Config().editor)
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
def list_items(locker, password):
    """
    Display the (unencrypted) names of all Secrets in the Locker
    :param locker:
    :param password:
    :return:
    """
    my_locker = Locker.find(locker, password)
    for sec in my_locker.list_secrets():
        print(f"{sec}")
    return


if __name__ == '__main__':
    main()
