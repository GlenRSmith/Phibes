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
from phibes.cli.locker.create import create_locker as create_locker_cmd
from phibes.cli.locker.delete import delete_locker as delete_locker_cmd

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class NaturalOrderGroup(click.Group):

    def list_commands(self, ctx):
        return self.commands.keys()


@click.group(cls=NaturalOrderGroup, context_settings=CONTEXT_SETTINGS)
@click.option(
    '--config',
    prompt='config path',
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


main.add_command(create_locker_cmd)
main.add_command(delete_locker_cmd)
main.add_command(item_edit_cmd)
main.add_command(item_get_cmd)
main.add_command(item_delete_cmd)
main.add_command(item_list_cmd)

if __name__ == '__main__':
    main()
