"""
Click interface to get Locker
"""

# core library modules
import abc
import copy
from os import environ
import pathlib

# third party packages
import click

# in-project modules
from phibes.cli.options import env_options, env_vars
from phibes.cli.options import locker_name_option, password_option
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
COMMON_OPTIONS = {
    'config': config_option,
    'locker': locker_name_option,
    'password': password_option
}

# These are the variables I need to unravel.
# locker name - not relevant in a "cwd" locker scenario.
# password
# editor (from config)
# store_path (from config) - not relevant in a "cwd" locker scenario.


class PhibesCommandBareBase(abc.ABC):
    """
    Base command class without options
    """

    options = {}

    def __init__(self):
        return

    @staticmethod
    def handle(*args, **kwargs) -> None:
        """
        Handler for CLI commands as implemented by each Command class
        """
        for kw in kwargs:
            if kwargs[kw]:
                environ[env_vars[kw]] = kwargs[kw]

    @classmethod
    def make_click_command(
            cls,
            cmd_name: str,
            initial_options: dict = None,
            *args, **kwargs
    ) -> click.command:
        """
        Creates a click command with specified options.
        Takes a command name, a python function, and a dict of options,
        and returns a named click.command
        """
        if not initial_options:
            initial_options = cls.options
        options = initial_options
        options.update(env_options)
        # Apply all the options to the func, the way the decorators would do
        for option in reversed(options.values()):
            option(cls.handle)
        return click.command(
            cmd_name, context_settings=dict(max_content_width=120)
        )(cls.handle)


# class PhibesCommandBase(PhibesCommandBareBase):
#     """
#     Base command class with default options included
#     """
#
#     options = copy.deepcopy(COMMON_OPTIONS)
#
#     def __init__(self):
#         super(PhibesCommandBase, self).__init__()
#
#     @staticmethod
#     def handle(*args, **kwargs) -> None:
#         """per-command handler callback"""
#         super(PhibesCommandBase, PhibesCommandBase).handle(*args, **kwargs)
#
#     @classmethod
#     def make_click_command(
#             cls,
#             cmd_name: str,
#             initial_options: dict = None,
#             *args, **kwargs
#     ) -> click.command:
#         """
#         Creates a click command with common options and specific options.
#         Takes a command name, a python function, and a dict of options,
#         and returns a named click.command
#         """
#         exclude_common = kwargs.pop('exclude_common', False)
#         if not exclude_common:
#             # Being careful not to mutate the module-level dict
#             options = copy.deepcopy(COMMON_OPTIONS)
#             # Merge the passed-in options dict into the common options dict.
#             # This exposes the ability to override any of the common options,
#             # such as making the `password` option issue a confirmation prompt.
#             options.update(initial_options)
#         else:
#             options = initial_options
#         return super().make_click_command(cmd_name, options)


class ConfigFileLoadingCmd(PhibesCommandBareBase):
    """
    Base command class for commands that allow passing in a config path
    """

    options = copy.deepcopy(COMMON_OPTIONS)

    def __init__(self):
        super(ConfigFileLoadingCmd, self).__init__()

    @staticmethod
    def handle(config_file: pathlib.Path, *args, **kwargs):
        """
        Callback for commands that rely on/allow for a config file,
        Should be invoked in the child handler before additional logic
        @param config_file: Config file path
        """
        super(ConfigFileLoadingCmd, ConfigFileLoadingCmd).handle(
            *args, **kwargs
        )
        load_config_file(config_file)
        return

    @classmethod
    def make_click_command(
            cls,
            cmd_name: str,
            initial_options: dict = None,
            *args, **kwargs
    ) -> click.command:
        """
        Creates a click command with common options and specific options.
        Takes a command name, a python function, and a dict of options,
        and returns a named click.command
        """
        exclude_common = kwargs.pop('exclude_common', False)
        if not exclude_common:
            # Being careful not to mutate the module-level dict
            options = copy.deepcopy(COMMON_OPTIONS)
            # Merge the passed-in options dict into the common options dict.
            # This exposes the ability to override any of the common options,
            # such as making the `password` option issue a confirmation prompt.
            options.update(initial_options)
        else:
            options = initial_options
        return super().make_click_command(cmd_name, options)
