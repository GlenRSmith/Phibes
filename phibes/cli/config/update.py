"""
Click interface to update Config
"""

# core library modules
import pathlib

# third party packages
import click

# in-project modules
from phibes.cli.command_base import PhibesCommand
from phibes.cli.errors import PhibesCliExistsError, PhibesCliError
from phibes.lib.errors import PhibesConfigurationError
from phibes.lib.config import ConfigModel, CONFIG_FILE_NAME
from phibes.lib.config import get_home_dir, load_config_file
from phibes.lib.config import write_config_file


default_store_path = None
default_editor = None


def populate_defaults():
    """
    If the user does have ~/CONFIG_FILE_NAME, use it to populate defaults
    """
    global default_store_path
    global default_editor
    try:
        load_config_file(get_home_dir().joinpath(CONFIG_FILE_NAME))
    except FileNotFoundError:
        pass
    try:
        current_conf = ConfigModel()
        default_store_path = current_conf.store_path
        default_editor = current_conf.editor
    except PhibesConfigurationError:
        pass


populate_defaults()


class UpdateConfigCmd(PhibesCommand):
    """
    Class for user command to update a configuration file
    """

    def __int__(self):
        super(UpdateConfigCmd, self).__init__()
        return

    @staticmethod
    def handle(
            path: pathlib.Path,
            store_path: pathlib.Path,
            editor: str,
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
                store_path=store_path, editor=editor
            )
            write_config_file(path, new_config, update=True)
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
        default=default_store_path
    ),
    'editor': click.option(
        '--editor',
        prompt='editor (for adding/updating encrypted items)',
        help='shell-invocable editor to use with the `edit` command',
        type=str,
        default=default_editor
    )
}


update_config_cmd = UpdateConfigCmd.make_click_command(
    'update-config', options, exclude_common=True
)
