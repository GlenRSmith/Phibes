"""
Support functions for command-line interface modules.
"""

# core library modules
import getpass
import pathlib
import subprocess

# third party packages
import click

# in-project modules
from phibes.cli.errors import PhibesCliError
from phibes.cli.errors import PhibesCliNotFoundError
from phibes.cli.errors import PhibesCliExistsError
from phibes.lib.config import CONFIG_FILE_NAME
from phibes.lib.config import get_editor, get_home_dir
from phibes.lib.errors import PhibesNotFoundError
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
    except PhibesNotFoundError as err:
        raise PhibesCliNotFoundError(
            f"can't find locker {locker_name} (could be password error)"
            f"\n{err}\n"
        )


def get_locker_anonymous(locker_path, password):
    """
    locally-used convenience function
    :param locker_path:
    :param password:
    :return:
    """
    try:
        return Locker.get_anonymous(locker_path, password)
    except PhibesNotFoundError as err:
        raise PhibesCliNotFoundError(
            f"can't find locker {locker_path} (could be password error)"
            f"\n{err}\n"
        )


def _create_item(
        locker_inst,
        item_name,
        template_name
):
    """
    Open a text editor to edit a new or existing item in a locker
    :param locker_inst: Instance of Locker (already authed)
    :param item_name: Name of item to edit
    :param template_name: Name of text template to start item with
    :return:
    """
    try:
        if locker_inst.get_item(item_name):
            raise PhibesCliExistsError(
                f"file for {item_name} already exists\n"
                f"please use the `edit` command to modify\n"
            )
    except PhibesNotFoundError:
        pass
    item = locker_inst.create_item(item_name=item_name)
    template_is_file = False
    if template_name:
        try:
            # try to get a template stored by that name
            item.content = locker_inst.get_item(template_name).content
        except PhibesNotFoundError:
            try:
                # try to find a file by that name
                item.content = pathlib.Path(template_name).read_text()
                template_is_file = True
            except PhibesNotFoundError:
                raise PhibesCliNotFoundError(f"{template_name} not found")
            except FileNotFoundError:
                raise PhibesCliNotFoundError(f"{template_name} not found")
    else:
        item.content = ''
    if not template_is_file:
        _user_edit_item(locker_inst, item)
    locker_inst.add_item(item)


def _user_edit_item(locker_inst: Locker, item):
    work_file = None
    try:
        work_file = locker_inst.path.joinpath(f"{item.name}.tmp")
        work_file.write_text(item.content)
        edit_cmd = f"{get_editor()} {work_file}"
        subprocess.call(edit_cmd, shell=True)
        # os.system(edit_cmd)
        item.content = work_file.read_text()
    except Exception as err:
        work_file = None
        raise PhibesCliError(err)
    finally:
        if work_file:
            work_file.unlink()
    return item


def _edit_item(locker_inst, item_name):
    """
    Open a text editor to edit an existing item in a locker
    :param locker_inst: Instance of Locker
    :param item_name: Name of item to edit
    :return:
    """
    try:
        item = locker_inst.get_item(item_name)
    except PhibesNotFoundError:
        raise PhibesCliNotFoundError(
            f"Item `{item_name}` not found"
        )
    _user_edit_item(locker_inst, item)
    locker_inst.update_item(item)


def create_item(
        locker_name,
        password,
        item_name,
        template_name
):
    """
    Open a text editor to edit a new or existing item in a locker
    :param locker_name: Name of the locker
    :param password: Password of the locker
    :param item_name: Name of item to edit
    :param template_name: Name of text template to start item with
    :return:
    """
    my_locker = get_locker(locker_name, password)
    return _create_item(my_locker, item_name, template_name)


def create_item_anon_locker(
        locker_path,
        password,
        item_name,
        template_name
):
    """
    Open a text editor to edit a new or existing item in a locker
    :param locker_path: Location of the locker
    :param password: Password of the locker
    :param item_name: Name of item to edit
    :param template_name: Name of text template to start item with
    :return:
    """
    my_locker = get_locker_anonymous(locker_path, password)
    return _create_item(my_locker, item_name, template_name)


def edit_item(locker_name: str, password: str, item_name: str):
    """
    Open a text editor to edit an existing item in a locker
    :param locker_name: Name of the locker
    :param password: Password of the locker
    :param item_name: Name of item to edit
    :return:
    """
    my_locker = get_locker(locker_name, password)
    return _edit_item(my_locker, item_name)


def edit_item_anon_locker(
        locker_path: pathlib.Path, password: str, item_name: str
):
    """
    Open a text editor to edit an existing item in a locker
    :param password: Password of the locker
    :param item_name: Name of item to edit
    :return:
    """
    my_locker = get_locker_anonymous(locker_path, password)
    return _edit_item(my_locker, item_name)


def present_list_items(locker_inst: Locker, verbose: bool):
    """Function to list items in a locker"""
    ret_val = f""
    items = locker_inst.list_items()
    if verbose:
        for sec in locker_inst.list_items():
            ret_val += f"{sec}"
    else:
        longest = 10
        for sec in items:
            longest = (longest, len(sec.name))[longest < len(sec.name)]
        ret_val += f"{'Item Name':>{longest+2}}\n"
        for sec in items:
            ret_val += f"{str(sec.name):>{longest+2}}\n"
    return ret_val


def _get_item(locker_inst: Locker, item_name: str):
    try:
        item = locker_inst.get_item(item_name)
    except PhibesNotFoundError:
        raise PhibesCliNotFoundError(f"can't find {item_name}")
    return item


def get_item_anon_locker(
        locker_path: pathlib.Path,
        password: str,
        item_name: str
):
    my_locker = get_locker_anonymous(locker_path, password)
    return _get_item(my_locker, item_name)


def get_item(
        locker_name: str,
        password: str,
        item_name: str
):
    my_locker = get_locker(locker_name, password)
    return _get_item(my_locker, item_name)


def delete_item(locker_name: str, password: str, item_name: str):
    try:
        my_locker = Locker.get(locker_name, password)
    except PhibesNotFoundError:
        raise PhibesCliNotFoundError(
            f"Locker {locker_name} not found"
        )
    try:
        my_locker.delete_item(item_name)
    except PhibesNotFoundError:
        raise PhibesCliNotFoundError(
            f"can't delete non-existing {item_name}"
        )
    return
