"""
pytest module for phibes_cli locker create command
"""

# Standard library imports
# Related third party imports
from click.testing import CliRunner
import pytest

# Local application/library specific imports
from phibes.cli.commands import Action, Target
from phibes.cli.commands import build_cli_app
from phibes.cli.handlers import create_locker
from phibes.cli.lib import main as main_group
from phibes.cli.options import crypt_choices
from phibes.lib.errors import PhibesNotFoundError
from phibes.model import Locker, LOCKER_FILE

# Local test imports
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import BaseAnonLockerTest
from tests.lib.test_helpers import ConfigLoadingTestClass


crypt_ids = list(crypt_choices.choice_dict.keys())


class TestNoName(BaseAnonLockerTest):

    password = "78CollECtion!CampCoolio"
    command_name = 'test_create_locker'
    target = Target.Locker
    action = Action.Create
    func = create_locker
    click_group = main_group

    def custom_setup(self, tmp_path):
        super(TestNoName, self).custom_setup(tmp_path)

    def custom_teardown(self, tmp_path):
        super(TestNoName, self).custom_teardown(tmp_path)

    def prep_and_run(self, arg_dict):
        # change the configured working path to the test directory
        update_config_option_default(
            self.click_group.commands[self.command_name],
            self.test_path
        )
        arg_list = [
            "--path", arg_dict.get('path', self.test_path),
            "--password", arg_dict.get('password', self.password),
            "--crypt_id", arg_dict.get('crypt_id')
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


class TestCreateLocker(ConfigLoadingTestClass):

    name = "new_locker"
    pw = "SmellyBeansVictor"
    test_config = {
        "editor": "vim",
        "store": {
            "store_type": "FileSystem",
            "store_path": "."
        }
    }
    target = Target.Locker
    action = Action.Create
    command_name = 'test_create_locker'
    func = create_locker
    click_group = main_group

    def custom_setup(self, tmp_path):
        super(TestCreateLocker, self).custom_setup(tmp_path)
        try:
            Locker.delete(self.name, self.pw)
        except PhibesNotFoundError:
            pass
        build_cli_app(
            command_dict={
                self.target: {
                    self.action: {
                        'name': self.command_name,
                        'func': self.__class__.func
                    }
                }
            },
            click_group=self.click_group,
            named_locker=True
        )

    def custom_teardown(self, tmp_path):
        super(TestCreateLocker, self).custom_teardown(tmp_path)
        try:
            Locker.delete(self.name, self.pw)
        except PhibesNotFoundError:
            pass

    @pytest.mark.parametrize("crypt_id", crypt_ids)
    @pytest.mark.positive
    def test_normal(self, setup_and_teardown, crypt_id):
        arg_list = [
            "--config", self.test_path,
            "--locker", self.name,
            "--password", self.pw,
            "--crypt_id", crypt_id
        ]
        result = CliRunner().invoke(
            cli=self.click_group.commands[self.command_name],
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
        update_config_option_default(
            self.click_group.commands[self.command_name], self.test_path
        )
        result = CliRunner().invoke(
            cli=self.click_group.commands[self.command_name],
            args=[
                "--locker", self.name,
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
