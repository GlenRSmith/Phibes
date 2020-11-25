"""
pytest module for phibes_cli locker create command
"""

# Standard library imports
import itertools

# Related third party imports
from click.testing import CliRunner
import pytest

# Local application/library specific imports
from phibes.cli.locker.create import create_locker_cmd, crypt_choices
from phibes.lib.errors import PhibesNotFoundError
from phibes.model import Locker
from phibes.phibes_cli import main

# Local test imports
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import ConfigLoadingTestClass


params = "command_instance,crypt_id"
command_instances = [create_locker_cmd, main.commands['create-locker']]
crypt_ids = list(crypt_choices.choice_dict.keys())
matrix_params = []
for element in itertools.product(command_instances, crypt_ids):
    matrix_params.append(element)


class TestCreateLocker(ConfigLoadingTestClass):

    name = "new_locker"
    pw = "SmellyBeansVictor"
    test_config = {
        "editor": "vim",
        "store_path": "."
    }

    def custom_setup(self, tmp_path):
        super(TestCreateLocker, self).custom_setup(tmp_path)
        try:
            Locker.delete(self.name, self.pw)
        except PhibesNotFoundError:
            pass
        return

    def custom_teardown(self, tmp_path):
        super(TestCreateLocker, self).custom_teardown(tmp_path)
        try:
            Locker.delete(self.name, self.pw)
        except PhibesNotFoundError:
            pass
        return

    @pytest.mark.parametrize(params, matrix_params)
    @pytest.mark.positive
    def test_normal(
            self, setup_and_teardown, command_instance, crypt_id
    ):
        result = CliRunner().invoke(
            command_instance,
            [
                "--config", self.test_path,
                "--locker", self.name,
                "--password", self.pw,
                "--crypt_id", crypt_id
            ]
        )
        print(f"\n\n{result=}\n")
        assert result.exit_code == 0
        assert "created" in result.output
        return

    @pytest.mark.parametrize(params, matrix_params)
    @pytest.mark.positive
    def test_normal_default_config(
            self, setup_and_teardown, command_instance, crypt_id
    ):
        update_config_option_default(command_instance, self.test_path)
        result = CliRunner().invoke(
            command_instance,
            [
                "--locker", self.name,
                "--password", self.pw,
                "--crypt_id", crypt_id
            ]
        )
        print(result)
        assert result.exit_code == 0
        assert "created" in result.output
        return
