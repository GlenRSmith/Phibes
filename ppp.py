#!/usr/bin/env python
"""
Command-line interface to python privacy playground features
"""

# core library modules

# third party packages
import click

# local project modules
from lib.locker import Locker
from lib.locker import Secret
from lib.utils import get_user_edit_content, write_user_edit_content


@click.group()
def main():
    pass


@main.group()
def locker():
    pass


@main.group()
def secret():
    pass


@main.command()
def config():
    print(f"configure me!")


@locker.command()
@click.option(
    '--name', prompt='Name of Locker', hide_input=False,
    confirmation_prompt=False
)
@click.option(
    '--password', prompt='New Locker password?', hide_input=True,
    confirmation_prompt=True
)
def create(name, password):
    new_locker = Locker(name, password, create=True)
    click.echo(f"Locker created {new_locker.locker_path}")
    return


@click.option(
    '--secret_text', prompt='Entry to be encrypted', hide_input=True,
    confirmation_prompt=True
)
@click.option(
    '--secret_name', prompt='Unique name for secret entry', hide_input=False,
    confirmation_prompt=False
)
@click.option(
    '--password', prompt='Existing Locker password', hide_input=True,
    confirmation_prompt=False
)
@click.option(
    '--locker_name', prompt='Name of Locker for storage', hide_input=False,
    confirmation_prompt=False
)
@secret.command()
def add(locker_name, password, secret_name, secret_text):
    """
    Add an encrypted secret to the named Locker
    :param locker_name: Name of the Locker
    :param password: Password assigned when Locker was created
    :param secret_name: Name of the new secret
    :param secret_text: Text of secret to be encrypted
    :return:
    """
    my_locker = Locker(locker_name, password)
    Secret(secret_name, my_locker, create=True, secret_text=secret_text)
    return


@click.option(
    '--secret_name', prompt='Unique name for secret entry', hide_input=False,
    confirmation_prompt=False
)
@click.option(
    '--password', prompt='Existing Locker password', hide_input=True,
    confirmation_prompt=False
)
@click.option(
    '--locker_name', prompt='Name of Locker for storage', hide_input=False,
    confirmation_prompt=False
)
@secret.command()
def edit(locker_name, password, secret_name):
    """
    Launch the user text editor, and, on exit, encrypt the
    contents of the file into a secret
    :param locker_name: Name of the Locker
    :param password: Password assigned when Locker was created
    :param secret_name: Name of the new secret
    :return:
    """
    my_locker = Locker(locker_name, password)
    existing = Secret.find(secret_name, my_locker)
    if existing:
        write_user_edit_content(existing)
    plaintext = get_user_edit_content()
    if existing:
        my_secret = Secret(secret_name, locker_name, create=False)
        my_secret.update(plaintext)
    else:
        Secret(
            secret_name, my_locker, create=True, secret_text=plaintext
        )
    return


@click.option(
    '--secret_name', prompt='Unique name for secret entry', hide_input=False,
    confirmation_prompt=False
)
@click.option(
    '--password', prompt='Existing Locker password', hide_input=True,
    confirmation_prompt=False
)
@click.option(
    '--locker_name', prompt='Name of Locker for storage', hide_input=False,
    confirmation_prompt=False
)
@secret.command()
def inspect(locker_name, password, secret_name):
    my_locker = Locker(locker_name, password)
    my_secret = Secret(secret_name, my_locker)
    click.echo(f"{my_secret.plaintext}")


@click.option(
    '--password', prompt='Locker password', hide_input=True,
    confirmation_prompt=False
)
@click.option(
    '--locker_name', prompt='Locker Name', hide_input=False,
    confirmation_prompt=False
)
@secret.command()
def list_all(locker_name, password):
    my_locker = Locker(locker_name, password)
    secrets = my_locker.list_secrets()
    for secret in secrets:
        print(f"{secret}")
    return


if __name__ == '__main__':
    main()
