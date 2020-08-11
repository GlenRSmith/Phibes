#!/usr/bin/env python
"""
Entity-centric command-line interface to phibes features
"""

# core library modules
import os
import sys

# third party packages
import click
from colorama import Fore, Style

# for purposes of the CLI project, lib is being treated as third-party!
from phibes.cli_lib import edit_item, get_user_editor
from phibes.lib.item import Item
from phibes.lib.locker import Locker
from phibes.lib.secret import Secret


@click.group()
def main():
    pass


@main.group()
def secret():
    pass


@secret.command()
@click.option('--locker_name', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to add',
    type=click.Choice(Locker.get_item_types()),
    default='secret'
)
@click.option('--item_name', prompt='Item name')
@click.option(
    '--file_path',
    prompt='Source file (with path)',
    default=os.getcwd()
)
@click.option(
    '--overwrite',
    prompt='Should an existing item be overwritten?',
    default=False
)
def add(
        locker_name,
        password,
        item_type,
        item_name,
        file_path,
        overwrite
):
    """
    Add an item to a Locker from a local file elsewhere on the local system
    :param locker_name:
    :param password:
    :param item_type:
    :param item_name:
    :param file_path:
    :param overwrite:
    :return:
    """
    my_locker = Locker.find(locker_name, password, hash_name=True)
    # never have the system proper access the file system outside of itself!
    with open(file_path, 'r') as item_file:
        content = item_file.read()
    item = Item(my_locker, item_name, item_type, content=content)
    if item.exists() and not overwrite:
        click.echo(f"Item {item_type} {item_name} already exists")
        return
    item.save(
        save_plain_text=False, save_encrypted=True, overwrite=overwrite
    )
    return


@secret.command()
@click.option('--locker_name', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to add',
    type=click.Choice(Locker.get_item_types()),
    default='secret'
)
@click.option('--item_name', prompt='Item name')
@click.option(
    '--overwrite',
    prompt='Should an existing item be overwritten?',
    default=False
)
@click.option(
    '--editor',
    prompt='Preferred Editor?',
    default=get_user_editor()
)
def edit(locker_name, password, item_type, item_name, overwrite, editor):
    """
    Open a text editor to edit a new or existing item in a locker
    :param locker_name: Name of the locker
    :param password: Password of the locker
    :param item_type: Type of item to edit
    :param item_name: Name of item to edit
    :param overwrite: Whether an existing item should be replaced
    :param editor: Text editor to use
    :return:
    """
    return edit_item(
        locker_name, password, item_type, item_name, overwrite, editor
    )


@secret.command()
@click.option('--locker_name', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option('--secret', prompt='Secret name')
def show(locker_name, password, secret):
    """
    Display the (unencrypted) contents of the named Secret
    :param locker_name:
    :param password:
    :param secret:
    :return:
    """
    my_locker = Locker.find(locker_name, password, hash_name=True)
    my_secret = Secret.find(my_locker, secret)
    if not my_secret.exists():
        click.echo(f"Secret {secret} does not exist")
    click.echo(f"{my_secret.content}")
    click.echo(f"{my_secret}")


@secret.command()
@click.option('--locker_name', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
def list_all(locker_name, password):
    """
    Display the (unencrypted) names of all Secrets in the Locker
    :param locker_name:
    :param password:
    :return:
    """
    my_locker = Locker.find(locker_name, password, hash_name=True)
    for sec in my_locker.list_secrets():
        print(f"{sec}")
    return


if __name__ == '__main__':
    main()
