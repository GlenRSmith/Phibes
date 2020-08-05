"""
Support functions for command-line interface modules.
"""

# core library modules
import os
import sys

# third party packages
from colorama import Fore, Style

# in-project modules
from . lib.config import Config
from . lib.item import Item
from . lib.locker import Locker


def make_str_bool(bool_str: str) -> bool:
    return not bool_str.lower().startswith('f')


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
        item = Item(my_locker, item_name, item_type, create=True)
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


def present_list_items(
        locker: str, password: str, item_type: str, verbose: bool
):
    ret_val = f""
    if item_type == 'all':
        item_type = None
    my_locker = Locker.find(locker, password)
    items = Item.find_all(my_locker, item_type)
    if verbose:
        for sec in my_locker.list_items():
            ret_val += f"{sec}"
    else:
        longest = 10
        for sec in items:
            longest = (longest, len(sec.name))[longest < len(sec.name)]
        ret_val += f"{'Item Type':>15}{'Item Name':>{longest+2}}\n"
        for sec in items:
            ret_val += (
                f"{str(sec.item_type).rjust(4, '-'):>15}"
                f"{str(sec.name):>{longest+2}}"
            )
    return ret_val
