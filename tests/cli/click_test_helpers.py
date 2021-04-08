"""
Helpers for testing click commands
"""

# Standard library imports

# Related third party imports
import click
from pathlib import Path

# Local application/library specific imports
from phibes.cli.commands import build_cli_app
from phibes.cli.commands import ANON_COMMAND_DICT, NAMED_COMMAND_DICT


class GroupProvider(object):
    """
    Base class that provides a "clean" click group for each child test
    """

    target = None
    action = None
    func = None
    command_name = None
    target_cmd = None

    @click.group()
    def click_test_group(self):
        pass

    def setup_command(self, force_named_lockers: bool = False):
        src_dict = (
            ANON_COMMAND_DICT, NAMED_COMMAND_DICT
        )[hasattr(self, 'locker_name') or force_named_lockers]
        self.command_name = src_dict[self.target][self.action]['name']
        self.func = src_dict[self.target][self.action]['func']
        build_cli_app(
            command_dict={
                self.target: {
                    self.action: src_dict[self.target][self.action]
                }
            },
            named_locker=hasattr(self, 'locker_name'),
            click_group=self.click_test_group
        )
        self.target_cmd = self.click_test_group.commands[self.command_name]


def update_config_option_default(command: click.command, new_path: Path):
    """
    Function to change the default on the `config` option with most commands
    Used in tests where `--config` isn't explicitly provided. Without calling
    this, the default will be the home directory of the current user.
    """
    for opt in command.params:
        if opt.name == 'config':
            opt.default = new_path.joinpath(opt.default.name)
