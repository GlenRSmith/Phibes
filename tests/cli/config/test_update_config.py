"""
pytest module for phibes_cli config update command
"""

# Standard library imports
import json
from pathlib import Path

# Related third party imports
from click.testing import CliRunner
import pytest

# Local application/library specific imports
from phibes.cli.config.update import update_config_cmd
from phibes.lib.errors import PhibesConfigurationError
from phibes.lib.config import CONFIG_FILE_NAME
from phibes.phibes_cli import main

# Local test imports
from tests.lib.test_helpers import ConfigLoadingTestClass


class TestUpdateConfig(ConfigLoadingTestClass):
    """
    Testing for the CLI update-config.
    """

    test_config = {
        "editor": "emacs",
        "store_path": "/etc"
    }
    bad_test_config = {
        "editor": "vim",
        "store_path": "/not/a/path/that/exists"
    }

    def custom_setup(self, tmp_path):
        super(TestUpdateConfig, self).custom_setup(tmp_path)
        return

    def custom_teardown(self, tmp_path):
        super(TestUpdateConfig, self).custom_teardown(tmp_path)
        return

    @pytest.mark.parametrize(
        "command_instance",
        [update_config_cmd, main.commands['update-config']]
    )
    @pytest.mark.positive
    def test_update_config(
            self, setup_and_teardown, command_instance
    ):
        target_loc = self.test_path.joinpath(
            CONFIG_FILE_NAME
        )
        assert target_loc.exists()
        result = CliRunner().invoke(
            command_instance,
            [
                "--path", self.test_path,
                "--store_path", self.test_config['store_path'],
                "--editor", self.test_config['editor']
            ]
        )
        assert result.exit_code == 0
        assert target_loc.exists()
        contents = json.loads(target_loc.read_text())
        assert contents['editor'] == self.test_config['editor']
        mem = Path(contents['store_path']).resolve()
        disk = Path(self.test_config['store_path']).resolve()
        assert (mem == disk)
        return

    @pytest.mark.parametrize(
        "command_instance",
        [update_config_cmd, main.commands['update-config']]
    )
    @pytest.mark.negative
    def test_update_bad_config(
            self, setup_and_teardown, command_instance
    ):
        target_loc = self.test_path.joinpath(
            CONFIG_FILE_NAME
        )
        assert target_loc.exists()
        result = CliRunner().invoke(
            command_instance,
            [
                "--path", self.test_path,
                "--store_path", self.bad_test_config['store_path'],
                "--editor", self.bad_test_config['editor']
            ]
        )
        assert result.exit_code == 1
        assert type(result.exception) == PhibesConfigurationError
        assert self.bad_test_config['store_path'] in str(result)
        assert target_loc.exists()
        return
