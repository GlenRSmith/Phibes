"""
Click interface to get Locker
"""

# core library modules
import abc
import copy
import getpass
import pathlib

# third party packages
import click

# in-project modules
from phibes.lib.config import CONFIG_FILE_NAME, load_config_file, get_home_dir


config_option = click.option(
    '--config',
    default=get_home_dir().joinpath(CONFIG_FILE_NAME),
    type=pathlib.Path,
    help=(
        f"Path to config file `{CONFIG_FILE_NAME}`, "
        f"defaults to user home"
    ),
    show_envvar=True,
    envvar="PHIBES_CONFIG",
)
locker_option = click.option(
    '--locker',
    prompt='Locker',
    type=str,
    default=getpass.getuser(),
    help="Name of locker, defaults to local OS username"
)
password_option = click.option(
    '--password',
    prompt='Password',
    help='Password used when Locker was created',
    hide_input=True
)


COMMON_OPTIONS = {
    'config': config_option,
    'locker': locker_option,
    'password': password_option
}


class PhibesCommandBase(abc.ABC):

    options = copy.deepcopy(COMMON_OPTIONS)

    def __init__(self):
        return

    # @property
    # @abc.abstractmethod
    # def options(self):
    #     return

    @staticmethod
    @abc.abstractmethod
    def handle(*args, **kwargs):
        return

    @classmethod
    def make_click_command(
            cls,
            cmd_name: str,
            initial_options: dict,
            exclude_common: bool = False
    ) -> click.command:
        """
        Creates a click command with common options and specific options.
        Takes a command name, a python function, and a dict of options,
        and returns a named click.command
        """
        if not exclude_common:
            # Being careful not to mutate the module-level dict
            options = copy.deepcopy(COMMON_OPTIONS)
            # Merge the passed-in options dict into the common options dict.
            # This exposes the ability to override any of the common options,
            # such as making the `password` option issue a confirmation prompt.
            options.update(initial_options)
        else:
            options = initial_options
        # Apply all the options to the func, the way the decorators would do
        for option in reversed(options.values()):
            option(cls.handle)
        return click.command(
            cmd_name, context_settings=dict(max_content_width=120)
        )(cls.handle)


class ConfigFileLoadingCmd(PhibesCommandBase):

    # @property
    # def options(self):
    #     return
    #
    def __init__(self):
        super(ConfigFileLoadingCmd, self).__init__()
        return

    @staticmethod
    def handle(config_file, *args, **kwargs):
        super(ConfigFileLoadingCmd, ConfigFileLoadingCmd).handle(
            *args, **kwargs
        )
        load_config_file(config_file)
        return
