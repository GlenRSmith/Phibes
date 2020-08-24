"""
Click interface to create Config
"""

# core library modules
import pathlib

# third party packages
import click

# in-project modules
from phibes.cli.lib import make_click_command
from phibes.cli.lib import PhibesExistsError, PhibesCliError
from phibes.lib.config import ConfigModel, CONFIG_FILE_NAME
from phibes.lib.config import write_config_file

options = {
    'path': click.option(
        '--path',
        prompt='Path to config file',
        help='Path on filesystem where config file will be written',
        type=pathlib.Path,
        default=CONFIG_FILE_NAME
    ),
    'store_path': click.option(
        '--store_path',
        prompt='Path to locker(s)',
        help='Path on filesystem where encrypted data will be written',
        type=pathlib.Path,
        default=ConfigModel.default_storage_path
    ),
    'editor': click.option(
        '--editor',
        prompt='editor (for adding/updating encrypted items)',
        help='shell-invocable editor to use with the `edit` command',
        type=str,
        default=ConfigModel.default_editor
    ),
    'hash_locker_names': click.option(
        '--hash',
        prompt='Do you want your stored locker names obfuscated?',
        type=bool,
        default=ConfigModel.default_hash_locker_names
    ),
}


def create(
        path: pathlib.Path,
        store_path: pathlib.Path,
        editor: str,
        hash: bool
):
    """
    Create a new Configuration file
    """
    try:
        new_config = ConfigModel(
            store_path=store_path, editor=editor, hash_names=hash
        )
        new_config.validate()
        write_config_file(path, new_config)
    except ValueError as err:
        raise PhibesCliError(err)
    except FileExistsError as err:
        raise PhibesExistsError(err)
    return


create_config_cmd = make_click_command(
    'create-config', create, options, exclude_common=True
)
