#!/usr/bin/env python
"""
Command-line interface to phibes utilities
"""

# core library modules
from pathlib import Path

# third party packages
import click

# for purposes of the CLI project, lib is being treated as third-party!
from phibes.model import Locker


@click.group()
def main():
    pass


@main.command()
@click.option('--name', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option('--filename', prompt='Name of file')
def encrypt(name, password, filename):
    my_locker = Locker.get(name=name, password=password)
    text_file = Path(my_locker.path).joinpath(filename)
    with text_file.open("r") as tf:
        content = tf.read()
        print(f"{content}")
    my_locker.encrypt(content)
    return


@main.command()
@click.option('--name', prompt='Name of Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option('--filename', prompt='Name of file')
def decrypt(name, password, filename):
    my_locker = Locker.get(name=name, password=password)
    crypt_file = Path(my_locker.path).joinpath(filename)
    with crypt_file.open("r") as cf:
        cipher_text = cf.read()
        print(f"{cipher_text}")
    my_locker.decrypt(cipher_text)
    return


if __name__ == '__main__':
    main()
