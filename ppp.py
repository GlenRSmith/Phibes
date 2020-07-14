#!/usr/bin/env python
"""
This is a script to set/get authentication credentials
"""

# core library modules
import os

# third party packages
import click

# local project modules
from lib import locker


@click.command()
@click.argument('name')
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True)
def create_locker(name, password):
    click.echo("Create a new user account and locker")
    new_locker = locker.Locker(name, password, create=True)
    click.echo(f"User account created {new_locker.auth_hash}")
    existing_locker = locker.Locker(name, password)
    hide = "BatteryHorseStaplerCorrect"
    click.echo(f"hide: {hide}")
    iv, hidden = locker.encrypt(
        existing_locker.crypt_key,
        hide
    )
    click.echo(f"existing_locker.crypt_key: {existing_locker.crypt_key}")
    click.echo(f"existing_locker.crypt_key: {existing_locker.crypt_key.hex()}")
    click.echo(f"encrypted form {hidden}")
    unhidden = locker.decrypt(
        existing_locker.crypt_key,
        iv,
        hidden
    ).decode()
    click.echo(f"unhidden {unhidden}")
    assert hide == unhidden
    return


@click.pass_context
def main(ctx, api_key, config_file):
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


@click.command()
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
    create_locker()
