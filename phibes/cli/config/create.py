"""
Click interface to create Config
"""

# core library modules
import pathlib

# third party packages
import click

# in-project modules
from phibes.cli.cli_config import CliConfig, CLI_CONFIG_FILE_NAME
from phibes.cli.cli_config import DEFAULT_EDITOR, get_home_dir
from phibes.cli.cli_config import write_config_file
from phibes.cli.command_base import PhibesCommand
from phibes.cli.errors import PhibesCliExistsError, PhibesCliError
from phibes.lib.config import DEFAULT_STORE_PATH


class CreateConfigCmd(PhibesCommand):
    """
    Class for user command to create a configuration file
    """

    def __int__(self):
        super(CreateConfigCmd, self).__init__()
        return

    @staticmethod
    def handle(
            path: pathlib.Path,
            *args, **kwargs
    ):
        """
        Create a new Configuration file
        """
        super(CreateConfigCmd, CreateConfigCmd).handle(*args, **kwargs)
        try:
            new_config = CliConfig(**kwargs)
            if not 'store_path' in kwargs:
                raise ConnectionError(kwargs)
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
        default=get_home_dir().joinpath(CLI_CONFIG_FILE_NAME)
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
}


create_config_cmd = CreateConfigCmd.make_click_command(
    'create-config', options
)
