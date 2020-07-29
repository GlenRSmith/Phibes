#!/usr/bin/env python
"""
Command-line interface to python privacy playground admin
"""

# core library modules
import json

# third party packages
import click

# In-project modules
from lib import config


@click.group()
def main():
    pass


@main.command()
def configure():
    print(f"configure me!")


@main.command()
def read_conf():
    my_conf = config.Config()
    click.echo(my_conf)


# @main.command()
# @click.option(
#     '--path',
#     prompt='installation path',
#     default=config.get_system_path().absolute()
# )
# @click.option(
#     '--proceed',
#     prompt='only default path supported, proceed?',
#     default=False
# )
# def init(path, proceed):
#     if proceed:
#         config.system_install(path)


if __name__ == '__main__':
    main()
