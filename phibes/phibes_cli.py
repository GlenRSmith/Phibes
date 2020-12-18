#!/usr/bin/env python
"""
Click-based command-line interface to phibes
"""

# core library modules

# third party packages

# in-project modules
from phibes.cli.config.create import create_config_cmd
from phibes.cli.config.update import update_config_cmd
from phibes.cli.item.create import create_item_cmd
from phibes.cli.item.delete import delete_item_cmd
from phibes.cli.item.edit import edit_item_cmd
from phibes.cli.item.list import list_items_cmd
from phibes.cli.item.get import get_item_cmd
from phibes.cli.lib import main
from phibes.cli.locker.create import create_locker_cmd
from phibes.cli.locker.delete import delete_locker_cmd
from phibes.cli.locker.get import get_locker_cmd


main.add_command(create_locker_cmd)
main.add_command(get_locker_cmd)
main.add_command(delete_locker_cmd)
main.add_command(edit_item_cmd)
main.add_command(create_item_cmd)
main.add_command(get_item_cmd)
main.add_command(list_items_cmd)
main.add_command(delete_item_cmd)
main.add_command(create_config_cmd)
main.add_command(update_config_cmd)


if __name__ == '__main__':
    main()
