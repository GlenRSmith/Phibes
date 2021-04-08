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
from phibes.cli.cli_config import CLI_CONFIG_FILE_NAME
from phibes.cli.commands import Action, Target
from phibes.lib.errors import PhibesConfigurationError

# Local test imports
from tests.cli.click_test_helpers import GroupProvider
from tests.lib.test_helpers import ConfigLoadingTestClass


class MixinConfigUpdate(GroupProvider):

    target = Target.Config
    action = Action.Update


class TestUpdateConfig(ConfigLoadingTestClass, MixinConfigUpdate):
    """
    Testing for the CLI update-config.
    """

    test_config = {
        "editor": "emacs",
        "store": {"store_type": "FileSystem", "store_path": "/etc"}
    }
    bad_test_config = {
        "editor": "vim",
        "store": {
            "store_type": "FileSystem",
            "store_path": "/not/a/path/that/exists"
        }
    }

    def custom_setup(self, tmp_path):
        super(TestUpdateConfig, self).custom_setup(tmp_path)
        target_loc = self.test_path.joinpath(CLI_CONFIG_FILE_NAME)
        if not target_loc.exists():
            invoke_args = [
                "--path", self.test_path,
                "--store_path", self.test_config['store']['store_path'],
                "--editor", self.test_config['editor']
            ]
            # easiest way to create a config
            CliRunner().invoke(
                cli=self.target_cmd,
                args=invoke_args
            )
        self.setup_command(force_named_lockers=True)

    def custom_teardown(self, tmp_path):
        super(TestUpdateConfig, self).custom_teardown(tmp_path)
        return

    @pytest.mark.positive
    def test_update_config(self, setup_and_teardown):
        target_loc = self.test_path.joinpath(CLI_CONFIG_FILE_NAME)
        assert target_loc.exists()
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
        )

    @pytest.mark.negative
    def test_update_bad_config(self, setup_and_teardown):
        target_loc = self.test_path.joinpath(CLI_CONFIG_FILE_NAME)
        assert target_loc.exists()
        invoke_args = [
            "--path", self.test_path,
            "--store_path", self.bad_test_config['store']['store_path'],
            "--editor", self.bad_test_config['editor']
        ]
        result = CliRunner().invoke(cli=self.target_cmd, args=invoke_args)
        assert result.exit_code == 1
        assert type(result.exception) == PhibesConfigurationError
        # on windows, "foo/bar" ends up as "foo\\\bar" in the exception
        for word in self.bad_test_config['store']['store_path'].split('/'):
            assert str(result.exception.message).count(word)
        assert target_loc.exists()
        return
