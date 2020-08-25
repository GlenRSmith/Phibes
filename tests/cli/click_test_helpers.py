"""
Helpers for testing click commands
"""

# Standard library imports

# Related third party imports
import click
from pathlib import Path

# Local application/library specific imports


def update_config_option_default(command: click.command, new_path: Path):
    """
    Function to change the default on the `config` option with most commands
    Used in tests where `--config` isn't explicitly provided. Without calling
    this, the default will be the home directory of the current user.
    """
    for opt in command.params:
        if opt.name == 'config':
            opt.default = new_path.joinpath(opt.default.name)
