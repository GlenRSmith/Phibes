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
from phibes.cli.cli_config import CLI_CONFIG_FILE_NAME
from phibes.lib.errors import PhibesConfigurationError
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
        target_loc = self.test_path.joinpath(CLI_CONFIG_FILE_NAME)
        assert not target_loc.exists()
        invoke_args = [
            "--path", self.test_path,
            "--store_path", self.test_config['store_path'],
            "--editor", self.test_config['editor']
        ]
        result = CliRunner().invoke(
            cli=main.commands['create-config'],
            args=invoke_args
        )
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
        target_loc = self.test_path.joinpath(CLI_CONFIG_FILE_NAME)
        assert target_loc.exists()
        invoke_args = [
            "--path", self.test_path,
            "--store_path", self.test_config['store_path'],
            "--editor", self.test_config['editor']
        ]
        result = CliRunner().invoke(
            cli=command_instance, args=invoke_args
        )
        assert result.exit_code == 0
        assert target_loc.exists()
        contents = json.loads(target_loc.read_text())
        assert contents['editor'] == self.test_config['editor']
        assert contents.get('store_path', None), (
            f"{result}"
            f"{result.exception}"
            f"{result.output}"
        )
        mem = Path(contents['store_path']).resolve()
        disk = Path(self.test_config['store_path']).resolve()
        assert (mem == disk)
        return

    @pytest.mark.parametrize(
        "command_instance", [update_config_cmd, main.commands['update-config']]
    )
    @pytest.mark.negative
    def test_update_bad_config(self, setup_and_teardown, command_instance):
        target_loc = self.test_path.joinpath(CLI_CONFIG_FILE_NAME)
        assert target_loc.exists()
        invoke_args = [
            "--path", self.test_path,
            "--store_path", self.bad_test_config['store_path'],
            "--editor", self.bad_test_config['editor']
        ]
        result = CliRunner().invoke(
            cli=command_instance,
            args=invoke_args
        )
        assert result.exit_code == 1
        assert type(result.exception) == PhibesConfigurationError
        # on windows, "foo/bar" ends up as "foo\\\bar" in the exception
        for word in self.bad_test_config['store_path'].split('/'):
            assert str(result.exception.message).count(word)
        assert target_loc.exists()
        return
