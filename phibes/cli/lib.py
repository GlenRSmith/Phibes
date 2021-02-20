"""
Support functions for command-line interface modules.
"""

# core library modules
from os import environ
import pathlib
import subprocess

# third party packages
import click

# in-project modules
from phibes.cli.errors import PhibesCliError
from phibes.cli.errors import PhibesCliExistsError
from phibes.cli.errors import PhibesCliNotFoundError
from phibes.lib.config import ConfigModel, load_config_file
from phibes.lib.errors import PhibesNotFoundError
from phibes.model import Item
from phibes.model import Locker

CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
    max_content_width=120
)


class NaturalOrderGroup(click.Group):
    """
    Custom group class to allow control over ordering of commands in CLI help
    """

    def list_commands(self, ctx):
        """
        Key to sorting behavior
        """
        return self.commands.keys()


def catch_phibes_cli(func):
    """
    decorator for command-line function error handling
    :param func: command-line function
    :return:
    """
    def inner_function(*args, **kwargs):
        """
        Inner decorator function
        """
        try:
            func(*args, **kwargs)
        except PhibesCliError as err:
            click.echo(err.message)
            exit(1)
    return inner_function


@click.group(cls=NaturalOrderGroup, context_settings=CONTEXT_SETTINGS)
def main():
    """
    Command-line interface to Phibes encrypted storage
    """
    pass


@catch_phibes_cli
def main_func():
    """
    This function exists exclusively to provide a place to apply the
    catch_phibes_cli function. It would be trivial and obvious to have
    the try-except from that decorator in the body of main, but as
    a decorator it can be easily applied more granularly (which was how
    it was originally developed, but decorating functions with that AND
    with click options was convoluted).
    """
    main()


def get_locker_args(*args, **kwargs) -> Locker:
    """
    Get a Locker using only named arguments
    Supports getting named and unnamed Lockers
    kwargs:
        password: str - Password for existing locker
        locker: str - The name of the locker
        path: str - The fs path to the locker, aka `storage_path`
        config: str - The fs path to the config file with `storage_path`
    Valid combinations
    - password, path
    - password, config
    - password, path, locker
    - password, config, locker
    """
    try:
        password = kwargs.get('password')
    except KeyError as err:
        raise PhibesCliError(f'missing required param {err}')
    if 'path' in kwargs:
        pth = kwargs.get('path')
    elif 'config' in kwargs:
        config = kwargs.get('config')
        load_config_file(config)
        pth = ConfigModel().store_path
    else:
        raise PhibesCliError(
            f'path param must be provided by param or in config file'
        )
    # locker name is optional, only settable from command-line
    locker = kwargs.get('locker', None)
    try:
        return Locker.get(password=password, name=locker, path=pth)
    except PhibesNotFoundError:
        err_name = (f" with {locker=}!", f"!")[locker is None]
        err = f"No locker found at {pth}{err_name}\n"
        raise PhibesCliNotFoundError(err)


def get_editor() -> str:
    """
    Get the user's configured editor, or raise an exception
    @return: editor as configured in environment
    """
    editor = environ.get('PHIBES_EDITOR', environ.get('EDITOR', None))
    if not editor:
        raise PhibesCliError(
            "`PHIBES_EDITOR` or `EDITOR` must be set in environment"
        )
    return editor


def get_work_path() -> pathlib.Path:
    """
    Get the user's configured work_path, or raise an exception
    @return: work_path as configured in environment
    """
    work_path = environ.get('PHIBES_WORK_PATH', None)
    if not work_path:
        raise PhibesCliError(
            "`PHIBES_WORK_PATH` must be set in environment"
        )
    return pathlib.Path(work_path)


def set_work_path(work_path: str):
    """
    Set the work_path in the current environment.
    Does not write to a file.
    """
    environ['PHIBES_WORK_PATH'] = work_path


EDITOR_FROM_ENV = True
WORKPATH_FROM_ENV = True


def user_edit_file(
        work_path: pathlib.Path, name: str, content: str
):
    if EDITOR_FROM_ENV:
        editor = get_editor()
    else:
        raise PhibesCliError('not implemented')
    work_file = work_path / f"{name}.tmp"
    try:
        work_file.write_text(content)
        edit_cmd = f"{editor} {work_file}"
        subprocess.call(edit_cmd, shell=True)
        return work_file.read_text()
    except Exception as err:
        work_file = None
        raise PhibesCliError(err)
    finally:
        if work_file:
            work_file.unlink()


def user_edit_local_item(item_name: str, initial_content: str = ''):
    if WORKPATH_FROM_ENV:
        work_path = get_work_path()
    else:
        raise PhibesCliError('not implemented')
    return user_edit_file(
        work_path=work_path, name=item_name, content=initial_content
    )


def user_edit_item(locker: Locker, item: Item):
    item.content = user_edit_file(
        work_path=pathlib.Path(locker.path),
        name=item.name,
        content=item.content
    )
    return item


def edit_item(locker: Locker, item_name: str):
    """
    Open a text editor to edit an existing item in a locker
    :param locker: Instance of locker
    :param item_name: Name of item to edit
    :return:
    """
    try:
        item = locker.get_item(item_name)
    except PhibesNotFoundError:
        raise PhibesCliNotFoundError(f"Item `{item_name}` not found")
    item.content = user_edit_file(
        work_path=pathlib.Path(locker.path),
        name=item.name,
        content=item.content
    )
    return locker.update_item(item)


def present_list_items2(items, verbose: bool):
    """Function to list items in a locker"""
    ret_val = f""
    if verbose:
        for sec in items:
            ret_val += f"{sec}"
    else:
        longest = 10
        for sec in items:
            longest = (longest, len(sec.name))[longest < len(sec.name)]
        ret_val += f"{'Item Name':>{longest+2}}\n"
        for sec in items:
            ret_val += f"{str(sec.name):>{longest+2}}\n"
    return ret_val


def present_list_items(locker_inst: Locker, verbose: bool):
    """Function to list items in a locker"""
    items = locker_inst.list_items()
    return present_list_items2(items, verbose)
