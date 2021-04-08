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
from phibes.cli.cli_config import CLI_CONFIG_FILE_NAME
from phibes.cli.commands import Action, Target
from phibes.lib.errors import PhibesConfigurationError

# Local test imports
from tests.cli.click_test_helpers import GroupProvider
from tests.lib.test_helpers import ConfigLoadingTestClass


class MixinConfigCreate(GroupProvider):

    target = Target.Config
    action = Action.Create


class TestCreateConfig(ConfigLoadingTestClass, MixinConfigCreate):
    """
    Testing for the CLI create-config.
    """

    test_config = {
        "editor": "vim",
        "store": {"store_type": "FileSystem", "store_path": "."}
    }
    bad_test_config = {
        "editor": "vim",
        "store": {
            "store_type": "FileSystem",
            "store_path": "/not/a/path/that/exists"
        }
    }

    def custom_setup(self, tmp_path):
        super(TestCreateConfig, self).custom_setup(tmp_path)
        try:
            self.test_path.joinpath(CLI_CONFIG_FILE_NAME).unlink()
        except FileNotFoundError:
            pass
        self.setup_command(force_named_lockers=True)

    def custom_teardown(self, tmp_path):
        super(TestCreateConfig, self).custom_teardown(tmp_path)
        try:
            self.test_path.joinpath(CLI_CONFIG_FILE_NAME).unlink()
        except FileNotFoundError:
            pass
        return

    @pytest.mark.positive
    def test_create_config(self, setup_and_teardown):
        target_loc = self.test_path.joinpath(CLI_CONFIG_FILE_NAME)
        assert not target_loc.exists()
        invoke_args = [
            "--path", self.test_path,
            "--store_path", self.test_config['store']['store_path'],
            "--editor", self.test_config['editor']
        ]
        result = CliRunner().invoke(cli=self.target_cmd, args=invoke_args)
        assert result.exit_code == 0, (
            f"{result}"
            f"{result.exception}"
            f"{result.output}"
        )
        assert target_loc.exists()
        contents = json.loads(target_loc.read_text())
        assert contents['editor'] == self.test_config['editor']
        assert contents.get('store', None), (
            f"{result}"
            f"{result.exception}"
            f"{result.output}"
        )
        assert (
                Path(contents['store']['store_path']).resolve() ==
                Path(self.test_config['store']['store_path']).resolve()
        ), (
            f"{result}"
            f"{result.exception}"
            f"{result.output}"
        )
        return

    @pytest.mark.negative
    def test_create_bad_config(self, setup_and_teardown):
        target_loc = self.test_path.joinpath(CLI_CONFIG_FILE_NAME)
        assert not target_loc.exists()
        result = CliRunner().invoke(
            self.target_cmd,
            [
                "--path", self.test_path,
                "--store_path", self.bad_test_config['store']['store_path'],
                "--editor", self.bad_test_config['editor']
            ]
        )
        assert result.exit_code == 1, (
            f'{result.output=}     \n'
            f'{result.exception=}     \n'
            f'{result.exit_code=}     \n'
        )
        assert type(result.exception) == PhibesConfigurationError, (
            f"{result=}"
            f"{result.output=}"
            f"{result.exception=}"
        )
        assert not target_loc.exists()
        return
