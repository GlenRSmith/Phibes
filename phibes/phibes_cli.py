#!/usr/bin/env python
"""
Click-based command-line interface to phibes
"""

# core library modules
import getpass
import pathlib

# third party packages
import click

# in-project modules
from phibes.cli.item.delete import delete_item as item_delete_cmd
from phibes.cli.item.edit import edit as item_edit_cmd
from phibes.cli.item.list import list_items as item_list_cmd
from phibes.cli.item.get import get_item as item_get_cmd
from phibes.cli.lib import make_click_command
from phibes.cli.lib import PhibesCliError
from phibes.cli.locker.create import create_locker_cmd
from phibes.cli.locker.delete import delete_locker_cmd
from phibes.cli.locker.get import get_locker_cmd


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class NaturalOrderGroup(click.Group):

    def list_commands(self, ctx):
        return self.commands.keys()


@click.group(cls=NaturalOrderGroup, context_settings=CONTEXT_SETTINGS)
@click.option(
    '--config',
    default=pathlib.Path.home().joinpath('.phibes.cfg')
)
@click.option('--locker', prompt='Locker', default=getpass.getuser())
@click.option('--password', prompt='Password', hide_input=True)
@click.pass_context
def main(ctx, config, locker, password):
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['locker'] = locker
    ctx.obj['password'] = password


@click.group()
def cli():
    """This is my parent description"""
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
    cli()


cli.add_command(get_locker_cmd)
cli.add_command(create_locker_cmd)
cli.add_command(delete_locker_cmd)

main.add_command(create_locker_cmd)
main.add_command(delete_locker_cmd)
main.add_command(item_edit_cmd)
main.add_command(item_get_cmd)
main.add_command(item_delete_cmd)
main.add_command(item_list_cmd)

if __name__ == '__main__':
    # main()
    main_shim()
