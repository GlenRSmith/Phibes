"""
Support functions for command-line interface modules.
"""

# core library modules
import os
import sys

# third party packages
from colorama import Fore, Style

# for purposes of the CLI project, lib is being treated as third-party!
from lib.config import Config
from lib.item import Item
from lib.locker import Locker


def get_user_editor():
    editor = Config().editor
    if not editor:
        print(
            Style.RESET_ALL
            + Style.BRIGHT
            + Fore.RED
            + "ERROR, NO EDITOR FOUND!\n"
            + Style.RESET_ALL
        )
        print("Please set an editor.")
        sys.exit(1)
    return editor


def edit_item(
        locker_name,
        password,
        item_type,
        item_name,
        overwrite,
        template_name,
        editor
):
    """
    Open a text editor to edit a new or existing item in a locker
    :param locker_name: Name of the locker
    :param password: Password of the locker
    :param item_type: Type of item to edit
    :param item_name: Name of item to edit
    :param overwrite: Whether an existing item should be replaced
    :param template_name: Name of text template to start item with
    :param editor: Text editor to use
    :return:
    """
    my_locker = Locker.find(locker_name, password)
    item = Item.find(my_locker, item_name, item_type)
    if item is None:
        item = Item.create(my_locker, item_name, item_type)
    elif not overwrite:
        raise FileExistsError(
            f"{locker_name}:{item_type}:{item_name} already exists"
        )
    work_file = my_locker.path.joinpath(
        f"{item_type}:{item_name}.tmp"
    )
    if template_name:
        template = Item.find(my_locker, template_name, 'template')
        work_file.write_text(template.content)
    os.system(f"{editor} {work_file}")
    item.content = work_file.read_text()
    item.save(overwrite=overwrite)
    work_file.unlink()
    return
