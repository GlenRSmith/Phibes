#!/usr/bin/env python
"""
Command-line interface to python privacy playground features
"""

# core library modules
import os

# third party packages
import click

# local project modules
from lib.locker import decrypt, encrypt
from lib.locker import Locker
from lib.locker import Secret


@click.group()
def main():
    pass


@main.group()
def locker():
    pass


@main.group()
def secret():
    pass


@locker.command()
@click.argument('name')
@click.option(
    '--password', prompt='New Locker password?', hide_input=True,
    confirmation_prompt=True
)
def create(name, password):
    click.echo("Create a new user account and locker")
    new_locker = Locker(name, password, create=True)
    click.echo(f"User account created {new_locker.auth_hash}")
    existing_locker = Locker(name, password)
    hide = "BatteryHorseStaplerCorrect"
    click.echo(f"hide: {hide}")
    iv, hidden = encrypt(
        existing_locker.crypt_key,
        hide
    )
    click.echo(f"existing_locker.crypt_key: {existing_locker.crypt_key}")
    click.echo(f"existing_locker.crypt_key: {existing_locker.crypt_key.hex()}")
    click.echo(f"encrypted form {hidden}")
    unhidden = decrypt(existing_locker.crypt_key, iv, hidden).decode()
    click.echo(f"unhidden {unhidden}")
    assert hide == unhidden
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
    my_secret = Secret(secret_name, my_locker)
    my_secret.create(secret_text)
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
    pw = my_secret.read()
    click.echo(f"unhidden {pw}")


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
