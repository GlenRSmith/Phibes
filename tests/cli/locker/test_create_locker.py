"""
pytest module for phibes_cli locker create command
"""

# Standard library imports

# Related third party imports
from click.testing import CliRunner
import pytest

# Local application/library specific imports
from phibes.cli.locker.create import create_locker_cmd
from phibes.lib.locker import Locker
from phibes.phibes_cli import main

# Local test imports
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.locker_helper import ConfigLoadingTestClass
from tests.lib.locker_helper import setup_and_teardown


used = setup_and_teardown


class TestCreateLocker(ConfigLoadingTestClass):

    name = "new_locker"
    pw = "SmellyBeansVictor"
    test_config = {
        "editor": "vim",
        "hash_locker_names": "False",
        "store_path": "."
    }

    def custom_setup(self, tmp_path):
        super(TestCreateLocker, self).custom_setup(tmp_path)
        try:
            Locker.delete(self.name, self.pw)
        except FileNotFoundError:
            pass
        return

    def custom_teardown(self):
        try:
            Locker.delete(self.name, self.pw)
        except FileNotFoundError:
            pass
        return

    @pytest.mark.parametrize(
        "command_instance", [create_locker_cmd, main.commands['create-locker']]
    )
    def test_normal(
            self, setup_and_teardown, command_instance
    ):
        result = CliRunner().invoke(
            command_instance,
            [
                "--config", self.test_path,
                "--locker", self.name,
                "--password", self.pw
            ]
        )
        assert result.exit_code == 0
        assert "created" in result.output
        return

    @pytest.mark.parametrize(
        "command_instance", [create_locker_cmd, main.commands['create-locker']]
    )
    def test_normal_default_config(
            self, setup_and_teardown, command_instance
    ):
        update_config_option_default(command_instance, self.test_path)
        result = CliRunner().invoke(
            command_instance,
            [
                "--locker", self.name,
                "--password", self.pw
            ]
        )
        assert result.exit_code == 0
        assert "created" in result.output
        return
