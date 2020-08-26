"""
Click interface to update Config
"""

# core library modules
import pathlib

# third party packages
import click

# in-project modules
from phibes.cli.command_base import PhibesCommandBase
from phibes.cli.lib import PhibesExistsError, PhibesCliError
from phibes.lib.config import ConfigModel, CONFIG_FILE_NAME
from phibes.lib.config import get_home_dir, load_config_file
from phibes.lib.config import write_config_file

try:
    load_config_file(get_home_dir().joinpath(CONFIG_FILE_NAME))
except FileNotFoundError:
    conf = ConfigModel(store_path='.', editor='vi', hash_names=True)
    write_config_file(get_home_dir().joinpath(CONFIG_FILE_NAME), conf)


current_conf = ConfigModel()


class UpdateConfigCmd(PhibesCommandBase):

    def __int__(self):
        super(UpdateConfigCmd, self).__init__()
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
        super(UpdateConfigCmd, UpdateConfigCmd).handle(
            *args, **kwargs
        )
        try:
            new_config = ConfigModel(
                store_path=store_path, editor=editor, hash_names=hash_names
            )
            write_config_file(path, new_config, update=True)
        except ValueError as err:
            raise PhibesCliError(err)
        except FileExistsError as err:
            raise PhibesExistsError(err)
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
        default=current_conf.store_path
    ),
    'editor': click.option(
        '--editor',
        prompt='editor (for adding/updating encrypted items)',
        help='shell-invocable editor to use with the `edit` command',
        type=str,
        default=current_conf.editor
    ),
    'hash_locker_names': click.option(
        '--hash_names',
        prompt='Do you want your stored locker names obfuscated?',
        type=bool,
        default=current_conf.hash_locker_names
    )
}


update_config_cmd = UpdateConfigCmd.make_click_command(
    'update-config', options, exclude_common=True
)
