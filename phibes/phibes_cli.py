#!/usr/bin/env python
"""
Click-based command-line interface to phibes
"""
# core library modules
# third party packages
# in-project modules
from phibes.cli.config.create import create_config_cmd
from phibes.cli.config.update import update_config_cmd
from phibes.cli.item.create import CreateItemNamedLocker
from phibes.cli.item.delete import DeleteItemNamedLocker
from phibes.cli.item.edit import EditItemNamedLocker
from phibes.cli.item.get import GetItemNamedLocker
from phibes.cli.item.list import ListItemsNamedLocker
from phibes.cli.lib import main, main_func
from phibes.cli.locker.create import CreateNamedLocker
from phibes.cli.locker.delete import DeleteNamedLocker
from phibes.cli.locker.get import GetNamedLocker

create = CreateNamedLocker.make_click_command('create')
info = GetNamedLocker.make_click_command('info')
delete = DeleteNamedLocker.make_click_command('delete')
create_item = CreateItemNamedLocker.make_click_command('create-item')
get_item = GetItemNamedLocker.make_click_command('get-item')
delete_item = DeleteItemNamedLocker.make_click_command('delete-item')
edit_item = EditItemNamedLocker.make_click_command('edit')
list_items = ListItemsNamedLocker.make_click_command('list')

main.add_command(create)
main.add_command(info)
main.add_command(delete)
main.add_command(edit_item)
main.add_command(create_item)
main.add_command(get_item)
main.add_command(list_items)
main.add_command(delete_item)
main.add_command(create_config_cmd)
main.add_command(update_config_cmd)


if __name__ == '__main__':
    main_func()
