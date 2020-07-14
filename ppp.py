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
@click.option('--password', prompt='New Locker password?', hide_input=True,
              confirmation_prompt=True)
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
    '--secret_text',
    prompt='Entry to be encrypted',
    hide_input=True,
    confirmation_prompt=True
)
@click.option(
    '--secret_name',
    prompt='Unique name for secret entry',
    hide_input=False,
    confirmation_prompt=False
)
@click.option(
    '--password',
    prompt='Existing Locker password',
    hide_input=True,
    confirmation_prompt=False
)
@click.option(
    '--locker_name',
    prompt='Name of Locker for storage',
    hide_input=False,
    confirmation_prompt=False
)
@secret.command()
def add(locker_name, password, secret_name, secret_text):
    my_locker = Locker(locker_name, password)
    click.echo(f"secret: {secret_text}")
    iv, hidden = encrypt(my_locker.crypt_key, secret_text)
    # click.echo(f"existing_locker.crypt_key: {my_locker.crypt_key}")
    # click.echo(f"existing_locker.crypt_key: {my_locker.crypt_key.hex()}")
    # click.echo(f"encrypted form {hidden}")
    unhidden = decrypt(my_locker.crypt_key, iv, hidden).decode()
    click.echo(f"unhidden {unhidden}")
    assert secret_text == unhidden
    return


@click.option(
    '--secret_name',
    prompt='Unique name for secret entry',
    hide_input=False,
    confirmation_prompt=False
)
@click.option(
    '--password',
    prompt='Existing Locker password',
    hide_input=True,
    confirmation_prompt=False
)
@click.option(
    '--locker_name',
    prompt='Name of Locker for storage',
    hide_input=False,
    confirmation_prompt=False
)
@secret.command()
def inspect(locker_name, password, secret_name):
    my_locker = Locker(locker_name, password)
    click.echo(f"secret: {secret_text}")
    iv, hidden = encrypt(my_locker.crypt_key, secret_text)
    unhidden = decrypt(my_locker.crypt_key, iv, hidden).decode()
    click.echo(f"unhidden {unhidden}")
    assert secret_text == unhidden
    return


@click.pass_context
def what(ctx, api_key, config_file):
    """
    This is a tool for managing a secure, local password locker.
    """
    filename = os.path.expanduser(config_file)

    if not api_key and os.path.exists(filename):
        with open(filename) as cfg:
            api_key = cfg.read()

    ctx.obj = {
        'api_key': api_key,
        'config_file': filename,
    }


@main.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo('Hello %s!' % name)


# @main.command()
# @click.argument('location')
# @click.pass_context
# def current(ctx, location):
    """
    Show the current weather for a location using OpenWeatherMap data.
    """
    # api_key = ctx.obj['api_key']
    # weather = current_weather(location, api_key)
    # print(f"The weather in {location} right now: {weather}.")


if __name__ == '__main__':
    main()
