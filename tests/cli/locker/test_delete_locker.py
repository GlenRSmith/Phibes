"""
pytest module for phibes_cli locker delete command
"""

# Standard library imports

# Related third party imports
from click.testing import CliRunner
import pytest

# Local application/library specific imports
from phibes import crypto
from phibes.phibes_cli import delete as delete_cmd
from phibes.lib.errors import PhibesNotFoundError
from phibes.model import Locker
from phibes.phibes_cli import main

# Local test imports
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import ConfigLoadingTestClass


class TestDeleteLocker(ConfigLoadingTestClass):

    name = "new_locker"
    pw = "SmellyBeansVictor"

    def custom_setup(self, tmp_path):
        super(TestDeleteLocker, self).custom_setup(tmp_path)
        try:
            Locker.delete(password=self.pw, name=self.name)
        except PhibesNotFoundError:
            pass
        crypt_id = crypto.list_crypts()[0]
        Locker.create(password=self.pw, crypt_id=crypt_id, name=self.name)

    def custom_teardown(self, tmp_path):
        super(TestDeleteLocker, self).custom_teardown(tmp_path)
        try:
            Locker.delete(password=self.pw, name=self.name)
        except PhibesNotFoundError:
            pass

    @pytest.mark.parametrize(
        "command_instance",
        [delete_cmd, main.commands['delete']]
    )
    @pytest.mark.positive
    def test_delete_locker_main(
            self, setup_and_teardown, command_instance
    ):
        inst = Locker.get(password=self.pw, name=self.name)
        assert inst
        result = CliRunner().invoke(
            cli=command_instance,
            args=[
                "--config", self.test_path,
                "--locker", self.name,
                "--password", self.pw
            ],
            input="y\n"
        )
        assert result.exit_code == 0, (
            f'{result.exception=}\n'
            f'{result.output=}\n'
        )
        with pytest.raises(PhibesNotFoundError):
            Locker.get(password=self.pw, name=self.name)
        return

    @pytest.mark.parametrize(
        "command_instance",
        [delete_cmd, main.commands['delete']]
    )
    @pytest.mark.positive
    def test_delete_locker_normal(
            self, setup_and_teardown, command_instance
    ):
        update_config_option_default(command_instance, self.test_path)
        assert Locker.get(password=self.pw, name=self.name)
        result = CliRunner().invoke(
            cli=command_instance,
            args=[
                "--locker", self.name,
                "--password", self.pw
            ],
            input="y\n"
        )
        assert result.exit_code == 0, (
            f'{result.exception=}\n'
            f'{result.output=}\n'
        )
        with pytest.raises(PhibesNotFoundError):
            Locker.get(password=self.pw, name=self.name)
        return
