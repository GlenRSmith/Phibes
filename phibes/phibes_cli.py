#!/usr/bin/env python
"""
Click-based command-line interface to phibes
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.item import commands as item_group
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
main.add_command(item_group.edit)
main.add_command(item_group.list_items)
main.add_command(item_group.ls)
main.add_command(item_group.show_item)
main.add_command(item_group.delete_item)

if __name__ == '__main__':
    main()
