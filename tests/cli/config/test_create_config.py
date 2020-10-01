"""
pytest module for phibes_cli config create command
"""

# Standard library imports
import json
from pathlib import Path

# Related third party imports
from click.testing import CliRunner
import pytest

# Local application/library specific imports
from phibes.cli.config.create import create_config_cmd
from phibes.lib.errors import PhibesConfigurationError
from phibes.lib.config import CONFIG_FILE_NAME
from phibes.phibes_cli import main

# Local test imports
from tests.lib.test_helpers import BaseTestClass


class TestCreateConfig(BaseTestClass):
    """
    Testing for the CLI create-config.
    """

    test_config = {
        "editor": "vim",
        "hash_locker_names": False,
        "store_path": "."
    }
    bad_test_config = {
        "editor": "vim",
        "hash_locker_names": False,
        "store_path": "/not/a/path/that/exists"
    }

    def custom_setup(self, tmp_path):
        super(TestCreateConfig, self).custom_setup(tmp_path)
        try:
            self.test_path.joinpath(CONFIG_FILE_NAME).unlink()
        except FileNotFoundError:
            pass
        return

    def custom_teardown(self, tmp_path):
        super(TestCreateConfig, self).custom_teardown(tmp_path)
        try:
            self.test_path.joinpath(CONFIG_FILE_NAME).unlink()
        except FileNotFoundError:
            pass
        return

    @pytest.mark.parametrize(
        "command_instance",
        [create_config_cmd, main.commands['create-config']]
    )
    @pytest.mark.positive
    def test_create_config(
            self, setup_and_teardown, command_instance
    ):
        target_loc = self.test_path.joinpath(
            CONFIG_FILE_NAME
        )
        assert not target_loc.exists()
        result = CliRunner().invoke(
            command_instance,
            [
                "--path", self.test_path,
                "--store_path", self.test_config['store_path'],
                "--editor", self.test_config['editor'],
                "--hash_names", self.test_config['hash_locker_names']
            ]
        )
        assert result.exit_code == 0
        assert target_loc.exists()
        contents = json.loads(target_loc.read_text())
        assert contents['editor'] == self.test_config['editor']
        mem = Path(contents['store_path']).resolve()
        disk = Path(self.test_config['store_path']).resolve()
        assert (mem == disk)
        mem = contents['hash_locker_names']
        disk = self.test_config['hash_locker_names']
        assert (mem == disk)
        return

    @pytest.mark.parametrize(
        "command_instance",
        [create_config_cmd, main.commands['create-config']]
    )
    @pytest.mark.negative
    def test_create_bad_config(
            self, setup_and_teardown, command_instance
    ):
        target_loc = self.test_path.joinpath(
            CONFIG_FILE_NAME
        )
        assert not target_loc.exists()
        result = CliRunner().invoke(
            command_instance,
            [
                "--path", self.test_path,
                "--store_path", self.bad_test_config['store_path'],
                "--editor", self.bad_test_config['editor'],
                "--hash_names", self.bad_test_config['hash_locker_names']
            ]
        )
        assert result.exit_code == 1
        assert type(result.exception) == PhibesConfigurationError
        assert not target_loc.exists()
        return
