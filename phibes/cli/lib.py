"""
Support functions for command-line interface modules.
"""

# core library modules
import os
import sys

# third party packages
import click
from colorama import Fore, Style

# in-project modules
from phibes.lib.config import Config
from phibes.lib.locker import Locker


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


def get_locker(locker_name, password):
    """
    locally-used convenience function
    :param locker_name:
    :param password:
    :return:
    """
    try:
        return Locker.find(locker_name, password)
    except FileNotFoundError:
        raise PhibesNotFoundError(
            f"can't find locker {locker_name} (could be password error)"
        )


class PhibesCliError(Exception):

    def __init__(self, *args):
        if args:
            self.message = f"Phibes error: {args[0]}"
        else:
            self.message = f"Phibes error: no more info"
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
            f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.RED}"
            f"ERROR, NO EDITOR FOUND!\n"
            f"{Style.RESET_ALL}"
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
    draft_content = ""
    my_locker = get_locker(locker_name, password)
    try:
        item = my_locker.get_item(item_name, item_type)
    except FileNotFoundError:
        if overwrite:
            raise PhibesNotFoundError(
                f"can't overwrite non-existing {item_type}:{item_name}"
            )
        else:
            item = None
    if item:
        if not overwrite:
            raise PhibesExistsError(
                f"file for {item_type}:{item_name} already exists\n"
                f"overwrite=True must be specified to update\n"
            )
        else:
            draft_content = item.content
    if template_name:
        try:
            template = my_locker.get_item(template_name, "template")
        except FileNotFoundError:
            raise PhibesNotFoundError(
                f"template:{template_name} not found"
            )
    else:
        template = None
    if template:
        if item:
            draft_content += (
                f"\nprevious content above, "
                f"template:{template_name} follows\n"
            )
        draft_content += template.content
    else:
        if template_name:
            item = my_locker.create_item(
                item_name=item_name,
                item_type=item_type,
                template_name=template_name
            )
            my_locker.add_item(item, allow_empty=True)
        else:
            item = my_locker.create_item(
                item_name=item_name, item_type=item_type
            )
    work_file = my_locker.path.joinpath(f"{item_type}:{item_name}.tmp")
    work_file.write_text(draft_content)
    try:
        os.system(f"{editor} {work_file}")
        # avoid creating/changing item in storage until after this point,
        # it would be 'astonishing' to the user to apply changes if
        # e.g. there was an exception before they edit the item
        if not item:
            item = my_locker.create_item(
                item_name=item_name, item_type=item_type
            )
        item.content = work_file.read_text()
        if item:
            my_locker.update_item(item)
        else:
            my_locker.add_item(item)
    except Exception as err:
        raise PhibesCliError(err)
    finally:
        work_file.unlink()
    return


def present_list_items(
        locker: str, password: str, item_type: str, verbose: bool
):
    ret_val = f""
    if item_type == 'all':
        item_type = None
    my_locker = get_locker(locker, password)
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


def get_item(
        locker_name: str,
        password: str,
        item_type: str,
        item_name: str
):
    my_locker = get_locker(locker_name, password)
    try:
        my_locker.get_item(item_name, item_type)
    except FileNotFoundError:
        raise PhibesNotFoundError(
            f"can't find {item_type}:{item_name}"
        )
    return


def delete_item(
        locker_name: str,
        password: str,
        item_type: str,
        item_name: str
):
    my_locker = get_locker(locker_name, password)
    try:
        my_locker.delete_item(item_name, item_type)
    except FileNotFoundError:
        raise PhibesNotFoundError(
            f"can't delete non-existing {item_type}:{item_name}"
        )
    return
