"""
Support functions for command-line interface modules.
"""

# core library modules
import pathlib
import subprocess

# third party packages
import click

# in-project modules
from phibes.cli.cli_config import CliConfig
from phibes.cli.errors import PhibesCliError

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


def get_editor() -> str:
    """
    Get the user's configured editor, or raise an exception
    @return: editor as configured in environment
    """
    editor = CliConfig().editor
    if not editor:
        raise PhibesCliError(
            "`PHIBES_EDITOR` or `EDITOR` must be set in environment"
        )
    return editor


def user_edit_file(
        work_path: str, name: str, content: str
):
    editor = CliConfig().editor
    work_file = pathlib.Path(work_path) / f"{name}.tmp"
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
    config = CliConfig()
    work_path = config.store['store_path']
    return user_edit_file(
        work_path=work_path, name=item_name, content=initial_content
    )


def present_item(item: dict) -> str:
    ret_val = "Item\n"
    ret_val += f"name: {item['name']}\n"
    ret_val += f"timestamp: {item['timestamp']}\n"
    ret_val += "content follows (between lines)\n"
    ret_val += "----------\n"
    ret_val += f"{item['body']}"
    ret_val += "\n----------\n"
    return ret_val


def present_list_items(items, verbose: bool):
    """Function to list items in a locker"""
    ret_val = ""
    if verbose:
        for sec in items:
            ret_val += present_item(sec)
    else:
        longest = 10
        for sec in items:
            longest = (
                longest, len(sec['name'])
            )[longest < len(sec['name'])]
        ret_val += f"{'Item Name':>{longest+2}}\n"
        for sec in items:
            ret_val += f"{str(sec['name']):>{longest+2}}\n"
    return ret_val
