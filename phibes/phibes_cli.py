#!/usr/bin/env python
"""
Click-based command-line interface to phibes
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.item.delete import delete_item_cmd
from phibes.cli.item.edit import edit_item_cmd
from phibes.cli.item.list import list_items_cmd
from phibes.cli.item.get import get_item_cmd
from phibes.cli.lib import PhibesCliError
from phibes.cli.locker.create import create_locker_cmd
from phibes.cli.locker.delete import delete_locker_cmd
from phibes.cli.locker.get import get_locker_cmd


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class NaturalOrderGroup(click.Group):

    def list_commands(self, ctx):
        return self.commands.keys()


@click.group(cls=NaturalOrderGroup, context_settings=CONTEXT_SETTINGS)
def main():
    """
    Command-line interface to Phibes encrypted storage
    """
    pass


def catch_phibes_cli(func):
    """
    decorator for command-line function error handling
    :param func: command-line function
    :return:
    """
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except PhibesCliError as err:
            click.echo(err.message)
            exit(1)
    return inner_function


@catch_phibes_cli
def main_shim():
    main()


main.add_command(create_locker_cmd)
main.add_command(get_locker_cmd)
main.add_command(delete_locker_cmd)
main.add_command(edit_item_cmd)
main.add_command(get_item_cmd)
main.add_command(list_items_cmd)
main.add_command(delete_item_cmd)


if __name__ == '__main__':
    main_shim()
