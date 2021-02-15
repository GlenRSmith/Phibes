#!/usr/bin/env python
"""
Click-based command-line interface to phibes
"""
# core library modules
# third party packages
# in-project modules
from phibes.cli.config.create import create_config_cmd
from phibes.cli.config.update import update_config_cmd
from phibes.cli.item.create import CreateItemNamedLockerCmd
from phibes.cli.item.delete import DeleteItemNamedLockerCmd
from phibes.cli.item.edit import edit_item_cmd
from phibes.cli.item.list import list_items_cmd
from phibes.cli.item.get import GetItemNamedLockerCmd
from phibes.cli.lib import main, main_func
from phibes.cli.locker.create import CreateNamedLockerCmd
from phibes.cli.locker.delete import DeleteNamedLockerCmd
from phibes.cli.locker.get import GetNamedLockerCmd

create = CreateNamedLockerCmd.make_click_command('create')
info = GetNamedLockerCmd.make_click_command('info')
delete = DeleteNamedLockerCmd.make_click_command('delete')
create_item = CreateItemNamedLockerCmd.make_click_command('create-item')
get_item = GetItemNamedLockerCmd.make_click_command('get-item')
delete_item = DeleteItemNamedLockerCmd.make_click_command('delete-item')

main.add_command(create)
main.add_command(info)
main.add_command(delete)
main.add_command(edit_item_cmd)
main.add_command(create_item)
main.add_command(get_item)
main.add_command(list_items_cmd)
main.add_command(delete_item)
main.add_command(create_config_cmd)
main.add_command(update_config_cmd)


if __name__ == '__main__':
    main_func()
