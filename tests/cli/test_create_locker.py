"""
pytest module for phibes_cli locker create command
"""

# Standard library imports
# Related third party imports
from click.testing import CliRunner
import pytest

# Local application/library specific imports
from phibes.cli.commands import Action, Target
from phibes.cli.options import crypt_choices
from phibes.lib.errors import PhibesNotFoundError
from phibes.model import Locker, LOCKER_FILE

# Local test imports
from tests.cli.click_test_helpers import GroupProvider
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import ConfigLoadingTestClass

crypt_ids = list(crypt_choices.choice_dict.keys())


class MixinLockerCreate(GroupProvider):

    target = Target.Locker
    action = Action.Create


class TestNoName(ConfigLoadingTestClass, MixinLockerCreate):

    password = "78CollECtion!CampCoolio"

    def custom_setup(self, tmp_path):
        super(TestNoName, self).custom_setup(tmp_path)
        self.setup_command()

    def custom_teardown(self, tmp_path):
        super(TestNoName, self).custom_teardown(tmp_path)

    def prep_and_run(self, arg_dict):
        # change the configured working path to the test directory
        update_config_option_default(self.target_cmd, self.test_path)
        arg_list = [
            "--path", arg_dict.get('path', self.test_path),
            "--password", arg_dict.get('password', self.password),
            "--crypt_id", arg_dict.get('crypt_id')
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
            f"{crypt_id=}\n"
            f"{result.exception=}\n"
            f"{result.output=}\n"
        )
        crypt = crypt_choices.choice_dict[crypt_id]
        assert f'Crypt ID {crypt}' in result.output
        inst = Locker.get(password=self.password, locker_name=None)
        assert (
                inst.data_model.storage.locker_file ==
                self.test_path / LOCKER_FILE
        )


class TestCreateLocker(ConfigLoadingTestClass, MixinLockerCreate):

    locker_name = "new_locker"
    pw = "SmellyBeansVictor"
    test_config = {
        "editor": "vim",
        "store": {"store_type": "FileSystem", "store_path": "."}
    }

    def custom_setup(self, tmp_path):
        super(TestCreateLocker, self).custom_setup(tmp_path)
        try:
            Locker.delete(self.locker_name, self.pw)
        except PhibesNotFoundError:
            pass
        self.setup_command()

    def custom_teardown(self, tmp_path):
        super(TestCreateLocker, self).custom_teardown(tmp_path)
        try:
            Locker.delete(self.locker_name, self.pw)
        except PhibesNotFoundError:
            pass

    @pytest.mark.parametrize("crypt_id", crypt_ids)
    @pytest.mark.positive
    def test_normal(self, setup_and_teardown, crypt_id):
        arg_list = [
            "--config", self.test_path,
            "--locker", self.locker_name,
            "--password", self.pw,
            "--crypt_id", crypt_id
        ]
        result = CliRunner().invoke(
            cli=self.target_cmd,
            args=arg_list,
            input="y\n"
        )
        assert result.exit_code == 0, (
            f"     {result.output=}     "
            f"     {result.exception=}     "
        )
        assert "created" in result.output

    @pytest.mark.parametrize("crypt_id", crypt_ids)
    @pytest.mark.positive
    def test_normal_default_config(self, setup_and_teardown, crypt_id):
        update_config_option_default(self.target_cmd, self.test_path)
        result = CliRunner().invoke(
            cli=self.target_cmd,
            args=[
                "--locker", self.locker_name,
                "--password", self.pw,
                "--crypt_id", crypt_id
            ],
            input="y\n"
        )
        assert result.exit_code == 0, (
            f"       {result.output}       "
            f"       {result.exit_code}       "
        )
        assert "created" in result.output
