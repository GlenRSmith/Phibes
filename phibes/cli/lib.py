"""
Support functions for command-line interface modules.
"""

# core library modules
import getpass
import os
import pathlib

# third party packages
import click

# in-project modules
from phibes.lib.config import ConfigModel, CONFIG_FILE_NAME
from phibes.lib.config import get_home_dir
from phibes.lib import errors
from phibes.lib.errors import PhibesNotFoundError
from phibes.model import Locker


COMMON_OPTIONS = {
    'config': click.option(
        '--config',
        default=get_home_dir().joinpath(CONFIG_FILE_NAME),
        type=pathlib.Path,
        help=(
            f"Path to config file `{CONFIG_FILE_NAME}`, "
            f"defaults to user home"
        ),
        show_envvar=True,
        envvar="PHIBES_CONFIG",
    ),
    'locker': click.option(
        '--locker',
        prompt='Locker',
        type=str,
        default=getpass.getuser(),
        help="Name of locker, defaults to local OS username"
    ),
    'password': click.option(
        '--password',
        prompt='Password',
        help='Password used when Locker was created',
        hide_input=True
    ),
}


def get_locker(locker_name, password):
    """
    locally-used convenience function
    :param locker_name:
    :param password:
    :return:
    """
    try:
        return Locker.find(locker_name, password)
    except errors.PhibesNotFoundError as err:
        raise PhibesCliNotFoundError(
            f"can't find locker {locker_name} (could be password error)"
            f"\n{err}\n"
        )


class PhibesCliError(errors.PhibesError):

    def __init__(self, *args):
        if args:
            self.message = f"Phibes error: {args[0]}"
        else:
            self.message = f"Phibes error: no more info"
        super().__init__(self.message)

    def __str__(self):
        msg = getattr(self, "message", "was raised")
        return f"{self.__class__}: {msg}"


class PhibesCliNotFoundError(PhibesCliError):
    pass


class PhibesCliExistsError(PhibesCliError):
    pass


class PhibesCliPasswordError(PhibesCliError):
    pass


def create_item(
        locker_name,
        password,
        item_type,
        item_name,
        template_name
):
    """
    Open a text editor to edit a new or existing item in a locker
    :param locker_name: Name of the locker
    :param password: Password of the locker
    :param item_type: Type of item to edit
    :param item_name: Name of item to edit
    :param template_name: Name of text template to start item with
    :return:
    """
    my_locker = get_locker(locker_name, password)
    try:
        if my_locker.get_item(item_name, item_type):
            raise PhibesCliExistsError(
                f"file for {item_type}:{item_name} already exists\n"
                f"please use the `edit` command to modify\n"
            )
    except errors.PhibesNotFoundError:
        pass
    if template_name:
        try:
            template = my_locker.get_item(template_name, item_type)
        except errors.PhibesNotFoundError:
            raise PhibesCliNotFoundError(
                f"{item_type}:{template_name} not found"
            )
    else:
        template = None
    work_file = my_locker.path.joinpath(f"{item_type}:{item_name}.tmp")
    work_file.write_text(getattr(template, 'content', ""))
    try:
        os.system(f"{ConfigModel().editor} {work_file}")
        item = my_locker.create_item(item_name=item_name, item_type=item_type)
        item.content = work_file.read_text()
        my_locker.add_item(item)
    except Exception as err:
        raise PhibesCliError(err)
    finally:
        work_file.unlink()
    return


def edit_item(
        locker_name: str,
        password: str,
        item_type: str,
        item_name: str
):
    """
    Open a text editor to edit an existing item in a locker
    :param locker_name: Name of the locker
    :param password: Password of the locker
    :param item_type: Type of item to edit
    :param item_name: Name of item to edit
    :return:
    """
    my_locker = get_locker(locker_name, password)
    try:
        item = my_locker.get_item(item_name, item_type)
    except PhibesNotFoundError:
        raise PhibesCliNotFoundError
    draft_content = item.content
    work_file = my_locker.path.joinpath(f"{item_type}:{item_name}.tmp")
    work_file.write_text(draft_content)
    try:
        os.system(f"{ConfigModel().editor} {work_file}")
        item.content = work_file.read_text()
        my_locker.update_item(item)
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
    except errors.PhibesNotFoundError:
        raise PhibesCliNotFoundError(
            f"can't find {item_type}:{item_name}"
        )
    return


def delete_item(
        locker_name: str,
        password: str,
        item_type: str,
        item_name: str
):
    try:
        my_locker = Locker(locker_name, password)
    except errors.PhibesNotFoundError:
        raise PhibesCliNotFoundError(
            f"Locker {locker_name} not found"
        )
    try:
        my_locker.delete_item(item_name, item_type)
    except errors.PhibesNotFoundError:
        raise PhibesCliNotFoundError(
            f"can't delete non-existing {item_type}:{item_name}"
        )
    return
