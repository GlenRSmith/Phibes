"""
pytest module for phibes_cli locker delete command
"""

# Standard library imports

# Related third party imports
from click.testing import CliRunner
import pytest

# Local application/library specific imports
from phibes.cli.commands import Action, Target
from phibes.cli.options import crypt_choices
from phibes import crypto
from phibes.lib.errors import PhibesNotFoundError
from phibes.model import Locker

# Local test imports
from tests.cli.click_test_helpers import GroupProvider
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import ConfigLoadingTestClass, PopulatedLocker


crypt_ids = list(crypt_choices.choice_dict.keys())


class MixinLockerDelete(GroupProvider):

    target = Target.Locker
    action = Action.Delete


class TestNoName(ConfigLoadingTestClass, MixinLockerDelete):

    password = "78CollECtion!CampCoolio"
    command_name = 'test_delete_locker'

    def custom_setup(self, tmp_path):
        super(TestNoName, self).custom_setup(tmp_path)
        self.setup_command()

    def custom_teardown(self, tmp_path):
        super(TestNoName, self).custom_teardown(tmp_path)

    def prep_and_run(self, arg_dict):
        self.my_locker = Locker.create(
            password=self.password,
            crypt_id=crypt_choices.choice_dict[arg_dict['crypt_id']],
            locker_name=None
        )
        # change the configured working path to the test directory
        update_config_option_default(self.target_cmd, self.test_path)
        arg_list = [
            "--path", arg_dict.get('path', self.test_path),
            "--password", arg_dict.get('password', self.password)
        ]
        return CliRunner().invoke(
            cli=self.target_cmd, args=arg_list, input="y\n"
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


class TestDeleteLocker(ConfigLoadingTestClass, MixinLockerDelete):

    locker_name = "new_locker"
    pw = "SmellyBeansVictor"

    def custom_setup(self, tmp_path):
        super(TestDeleteLocker, self).custom_setup(tmp_path)
        try:
            Locker.delete(password=self.pw, locker_name=self.locker_name)
        except PhibesNotFoundError:
            pass
        crypt_id = crypto.list_crypts()[0]
        Locker.create(
            password=self.pw, crypt_id=crypt_id, locker_name=self.locker_name
        )
        self.setup_command()

    def custom_teardown(self, tmp_path):
        super(TestDeleteLocker, self).custom_teardown(tmp_path)
        try:
            Locker.delete(password=self.pw, locker_name=self.locker_name)
        except PhibesNotFoundError:
            pass

    @pytest.mark.parametrize("crypt_id", crypt_ids)
    @pytest.mark.positive
    def test_delete_locker_main(self, setup_and_teardown, crypt_id):
        inst = Locker.get(password=self.pw, locker_name=self.locker_name)
        assert inst
        result = CliRunner().invoke(
            cli=self.target_cmd,
            args=[
                "--config", self.test_path,
                "--locker", self.locker_name,
                "--password", self.pw
            ],
            input="y\n"
        )
        assert result.exit_code == 0, (
            f'{result.exception=}\n'
            f'{result.output=}\n'
        )
        with pytest.raises(PhibesNotFoundError):
            Locker.get(password=self.pw, locker_name=self.locker_name)
        return

    @pytest.mark.parametrize("crypt_id", crypt_ids)
    @pytest.mark.positive
    def test_delete_locker_normal(self, setup_and_teardown, crypt_id):
        update_config_option_default(self.target_cmd, self.test_path)
        assert Locker.get(password=self.pw, locker_name=self.locker_name)
        result = CliRunner().invoke(
            cli=self.target_cmd,
            args=["--locker", self.locker_name, "--password", self.pw],
            input="y\n"
        )
        assert result.exit_code == 0, (
            f'{result.exception=}\n'
            f'{result.output=}\n'
        )
        with pytest.raises(PhibesNotFoundError):
            Locker.get(password=self.pw, locker_name=self.locker_name)


class TestDeletePopulated(PopulatedLocker, MixinLockerDelete):

    def custom_setup(self, tmp_path):
        super(TestDeletePopulated, self).custom_setup(tmp_path)
        self.setup_command()

    def custom_teardown(self, tmp_path):
        super(TestDeletePopulated, self).custom_teardown(tmp_path)

    def invoke(self):
        """
        Helper method for often repeated code in test methods
        :return:
        """
        return CliRunner().invoke(
            cli=self.target_cmd,
            args=[
                "--config", self.test_path,
                "--locker", self.locker_name,
                "--password", self.password
            ],
            input="y\n"
        )

    @pytest.mark.positive
    def test_delete(self, setup_and_teardown):
        result = self.invoke()
        assert result.exit_code == 0, (
            f"      {self.locker_name=}      "
            f"      {result=}      "
        )
