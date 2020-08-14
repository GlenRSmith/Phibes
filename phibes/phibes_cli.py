#!/usr/bin/env python
"""
Click-based command-line interface to phibes
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.item.delete import delete_item as item_delete_cmd
from phibes.cli.item.edit import edit as item_edit_cmd
from phibes.cli.item.list import list_items as item_list_cmd
from phibes.cli.item.get import get_item as item_get_cmd
from phibes.cli.locker import commands as locker_group

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class NaturalOrderGroup(click.Group):

    def list_commands(self, ctx):
        return self.commands.keys()


@click.group(cls=NaturalOrderGroup, context_settings=CONTEXT_SETTINGS)
def main():
    pass


main.add_command(locker_group.create_locker)
main.add_command(locker_group.delete_locker)
main.add_command(item_edit_cmd)
main.add_command(item_get_cmd)
main.add_command(item_delete_cmd)
main.add_command(item_list_cmd)
# main.add_command(item_group.list_items)
# main.add_command(item_group.ls)
# main.add_command(item_group.delete_item)

if __name__ == '__main__':
    main()
