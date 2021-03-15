"""
pytest module for phibes_cli locker delete command
"""

# Standard library imports

# Related third party imports
from click.testing import CliRunner
import pytest

# Local application/library specific imports
from phibes.cli.commands import Action, Target
from phibes.cli import handlers
from phibes.cli.lib import main as main_anon
from phibes.cli.options import crypt_choices
from phibes import crypto
from phibes.lib.errors import PhibesNotFoundError
from phibes.model import Locker
from phibes.phibes_cli import main

# Local test imports
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import BaseAnonLockerTest
from tests.lib.test_helpers import ConfigLoadingTestClass


crypt_ids = list(crypt_choices.choice_dict.keys())


class TestNoName(BaseAnonLockerTest):

    password = "78CollECtion!CampCoolio"
    command_name = 'test_delete_locker'
    target = Target.Locker
    action = Action.Delete
    func = handlers.delete_locker
    click_group = main_anon

    def custom_setup(self, tmp_path):
        super(TestNoName, self).custom_setup(tmp_path)

    def custom_teardown(self, tmp_path):
        super(TestNoName, self).custom_teardown(tmp_path)

    def prep_and_run(self, arg_dict):
        self.my_locker = Locker.create(
            password=self.password,
            crypt_id=crypt_choices.choice_dict[arg_dict['crypt_id']],
            locker_name=None
        )
        # change the configured working path to the test directory
        update_config_option_default(
            self.click_group.commands[self.command_name],
            self.test_path
        )
        arg_list = [
            "--path", arg_dict.get('path', self.test_path),
            "--password", arg_dict.get('password', self.password)
        ]
        return CliRunner().invoke(
            cli=self.click_group.commands[self.command_name],
            args=arg_list,
            input="y\n"
        )

    @pytest.mark.parametrize("crypt_id", crypt_ids)
    @pytest.mark.positive
    def test_success(self, crypt_id, setup_and_teardown):
        result = self.prep_and_run({'crypt_id': str(crypt_id)})
        assert result
        assert result.exit_code == 0, (
            f"{crypt_id=}\n{result.exception=}\n{result.output=}\n"
        )
        with pytest.raises(PhibesNotFoundError):
            Locker.get(password=self.password, locker_name=None)


class TestDeleteLocker(ConfigLoadingTestClass):

    name = "new_locker"
    pw = "SmellyBeansVictor"

    def custom_setup(self, tmp_path):
        super(TestDeleteLocker, self).custom_setup(tmp_path)
        try:
            Locker.delete(password=self.pw, locker_name=self.name)
        except PhibesNotFoundError:
            pass
        crypt_id = crypto.list_crypts()[0]
        Locker.create(
            password=self.pw, crypt_id=crypt_id, locker_name=self.name
        )

    def custom_teardown(self, tmp_path):
        super(TestDeleteLocker, self).custom_teardown(tmp_path)
        try:
            Locker.delete(password=self.pw, locker_name=self.name)
        except PhibesNotFoundError:
            pass

    @pytest.mark.parametrize(
        "command_instance",
        [main.commands['delete']]
    )
    @pytest.mark.positive
    def test_delete_locker_main(
            self, setup_and_teardown, command_instance
    ):
        inst = Locker.get(password=self.pw, locker_name=self.name)
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
            Locker.get(password=self.pw, locker_name=self.name)
        return

    @pytest.mark.parametrize(
        "command_instance",
        [main.commands['delete']]
    )
    @pytest.mark.positive
    def test_delete_locker_normal(
            self, setup_and_teardown, command_instance
    ):
        update_config_option_default(command_instance, self.test_path)
        assert Locker.get(password=self.pw, locker_name=self.name)
        result = CliRunner().invoke(
            cli=command_instance,
            args=["--locker", self.name, "--password", self.pw],
            input="y\n"
        )
        assert result.exit_code == 0, (
            f'{result.exception=}\n'
            f'{result.output=}\n'
        )
        with pytest.raises(PhibesNotFoundError):
            Locker.get(password=self.pw, locker_name=self.name)
        return
