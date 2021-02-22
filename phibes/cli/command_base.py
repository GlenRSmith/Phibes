"""
Click interface command helpers
"""

# core library modules
import abc
from os import environ
import pathlib

# third party packages
import click

# in-project modules
from phibes.cli.options import env_options, env_vars
from phibes.lib.config import CONFIG_FILE_NAME
from phibes.cli.cli_config import get_home_dir


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


class PhibesCommand(abc.ABC):
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
            if kwargs[kw] and kw in env_vars:
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
