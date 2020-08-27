"""
Click interface to create Config
"""

# core library modules
import pathlib

# third party packages
import click

# in-project modules
from phibes.cli.command_base import PhibesCommandBase
from phibes.cli.lib import PhibesCliExistsError, PhibesCliError
from phibes.lib.config import ConfigModel, CONFIG_FILE_NAME
from phibes.lib.config import DEFAULT_EDITOR, DEFAULT_HASH_LOCKER_NAMES
from phibes.lib.config import DEFAULT_STORE_PATH
from phibes.lib.config import get_home_dir, write_config_file


class CreateConfigCmd(PhibesCommandBase):

    def __int__(self):
        super(CreateConfigCmd, self).__init__()
        return

    @staticmethod
    def handle(
            path: pathlib.Path,
            store_path: pathlib.Path,
            editor: str,
            hash_names: bool,
            *args, **kwargs
    ):
        """
        Create a new Configuration file
        """
        super(CreateConfigCmd, CreateConfigCmd).handle(
            *args, **kwargs
        )
        try:
            new_config = ConfigModel(
                store_path=store_path, editor=editor, hash_names=hash_names
            )
            new_config.validate()
            write_config_file(path, new_config)
        except ValueError as err:
            raise PhibesCliError(err)
        except FileExistsError as err:
            raise PhibesCliExistsError(err)
        return


options = {
    'path': click.option(
        '--path',
        prompt='Path to config file',
        help='Path on filesystem where config file will be written',
        type=pathlib.Path,
        default=get_home_dir().joinpath(CONFIG_FILE_NAME)
    ),
    'store_path': click.option(
        '--store_path',
        prompt='Path to locker(s)',
        help='Path on filesystem where encrypted data will be written',
        type=pathlib.Path,
        default=get_home_dir().joinpath(DEFAULT_STORE_PATH)
    ),
    'editor': click.option(
        '--editor',
        prompt='editor (for adding/updating encrypted items)',
        help='shell-invocable editor to use with the `edit` command',
        type=str,
        default=DEFAULT_EDITOR
    ),
    'hash_locker_names': click.option(
        '--hash_names',
        prompt='Do you want your stored locker names obfuscated?',
        type=bool,
        default=DEFAULT_HASH_LOCKER_NAMES
    ),
}


create_config_cmd = CreateConfigCmd.make_click_command(
    'create-config', options, exclude_common=True
)
