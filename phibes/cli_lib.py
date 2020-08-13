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


class PhibesCliError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
        super().__init__(self.message)

    def __str__(self):
        msg = getattr(self, "message", "was raised")
        return f"{self.__class__}: {msg}"


class PhibesNotFoundError(PhibesCliError):
    pass


class PhibesExistsError(PhibesCliError):
    pass


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
    item = my_locker.get_item(item_name, item_type)
    if item:
        if not overwrite:
            raise FileExistsError(
                f"file for {item_type}:{item_name} already exists"
                f"overwrite True must be specified to replace"
            )
        else:
            if template_name:
                template = my_locker.get_item(template_name, 'template')
                item.content += (
                        f"\nprevious content above\n"
                        f"template {template_name} follows\n"
                        f"{template.content}"
                    )
                my_locker.update_item(item)
    else:
        item = my_locker.create_item(
            item_name=item_name,
            item_type=item_type,
            template_name=template_name
        )
        my_locker.add_item(item)
    work_file = my_locker.path.joinpath(
        f"{item_type}:{item_name}.tmp"
    )
    work_file.write_text(item.content)
    os.system(f"{editor} {work_file}")
    item.content = work_file.read_text()
    my_locker.update_item(item)
    work_file.unlink()
    return


def present_list_items(
        locker: str, password: str, item_type: str, verbose: bool
):
    ret_val = f""
    if item_type == 'all':
        item_type = None
    my_locker = Locker.find(locker, password)
    if not my_locker:
        raise FileNotFoundError(f"No locker {locker} found")
    items = my_locker.find_all(item_type, filter_include=True)
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
                f"{str(sec.item_type).rjust(4, ' '):>15}"
                f"{str(sec.name):>{longest+2}}\n"
            )
    return ret_val
