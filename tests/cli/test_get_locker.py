"""
pytest module for phibes_cli locker get command
"""

# Standard library imports
import itertools
from pathlib import Path

# Related third party imports
from click.testing import CliRunner
import pytest

# Target application/library specific imports
from phibes.cli import PhibesCliNotFoundError
from phibes.cli.commands import Action, Target
from phibes.crypto import list_crypts
from phibes.lib.config import ConfigModel
from phibes.lib.errors import PhibesAuthError
from phibes.model import Locker, LOCKER_FILE

# Local test imports
from tests.cli.click_test_helpers import GroupProvider
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import ConfigLoadingTestClass
from tests.lib.test_helpers import PopulatedLocker


params = "crypt_id,config_arg"
include_config_arg = [False, True]
matrix_params = []
for element in itertools.product(list_crypts(), include_config_arg):
    matrix_params.append(element)


class MixinLockerGet(GroupProvider):

    target = Target.Locker
    action = Action.Get


class TestNoName(ConfigLoadingTestClass, MixinLockerGet):

    password = "78CollECtion!CampCoolio"

    def custom_setup(self, tmp_path):
        super(TestNoName, self).custom_setup(tmp_path)
        self.setup_command()

    def custom_teardown(self, tmp_path):
        super(TestNoName, self).custom_teardown(tmp_path)

    def prep_and_run(self, arg_dict):
        self.my_locker = Locker.create(
            password=self.password,
            crypt_id=arg_dict['crypt_id'],
            locker_name=None
        )
        # change the configured working path to the test directory
        update_config_option_default(self.target_cmd, self.test_path)
        arg_list = [
            "--path", arg_dict.get('path', self.test_path),
            "--password", arg_dict.get('password', self.password)
        ]
        return CliRunner().invoke(cli=self.target_cmd, args=arg_list)

    @pytest.mark.parametrize("crypt_id", list_crypts())
    @pytest.mark.positive
    def test_found(self, crypt_id, setup_and_teardown):
        result = self.prep_and_run({'crypt_id': crypt_id})
        assert result
        assert result.exit_code == 0, (
            f"{crypt_id=}\n"
            f"{result.exception=}\n"
            f"{result.output=}\n"
        )
        assert f'Crypt ID {crypt_id}' in result.output
        inst = Locker.get(password=self.password, locker_name=None)
        assert (
                inst.data_model.storage.locker_file ==
                self.test_path / LOCKER_FILE
        )


class TestAllCryptTypes(PopulatedLocker, MixinLockerGet):

    def custom_setup(self, tmp_path):
        super(TestAllCryptTypes, self).custom_setup(tmp_path)
        self.setup_command()

    def custom_teardown(self, tmp_path):
        super(TestAllCryptTypes, self).custom_teardown(tmp_path)

    @pytest.mark.positive
    def test_good(self, tmp_path):
        for name in self.lockers.keys():
            inst = Locker.get(password=self.password, locker_name=name)
            assert inst


class TestMatrixHashed(PopulatedLocker, MixinLockerGet):

    def custom_setup(self, tmp_path):
        super(TestMatrixHashed, self).custom_setup(tmp_path)
        self.setup_command()

    def custom_teardown(self, tmp_path):
        super(TestMatrixHashed, self).custom_teardown(tmp_path)

    def prep_and_run(self, config_arg, arg_dict):
        if config_arg:
            arg_list = ["--config", self.test_path]
        else:
            arg_list = []
        # change the configured working path to the test directory
        update_config_option_default(self.target_cmd, self.test_path)
        # get the current config
        config = ConfigModel()
        # persist the changed config
        self.update_config(config)
        arg_list += [
            "--locker", arg_dict.get('name', self.locker_name),
            "--password", arg_dict.get('password', self.password)
        ]
        assert 'editor' not in arg_list
        assert '--editor' not in arg_list
        ret_val = CliRunner().invoke(
            cli=self.target_cmd, args=arg_list
        )
        return ret_val

    @pytest.mark.parametrize(params, matrix_params)
    @pytest.mark.positive
    def test_found(self, crypt_id, config_arg, setup_and_teardown):
        all_lockers = list(self.lockers.keys()) + [self.locker_name]
        for lck in all_lockers:
            result = self.prep_and_run(config_arg, {'name': lck})
            assert result
            assert result.exit_code == 0, (
                f"{config_arg=}\n"
                f"{result.exception=}\n"
                f"{result.output=}\n"
            )
            inst = Locker.get(password=self.password, locker_name=lck)
            assert (
                    inst.data_model.storage.locker_file ==
                    self.test_path / inst.locker_id / LOCKER_FILE
            )
            # alert if tests are messing up actual user home dir
            assert not Path.home().joinpath(self.locker_name).exists()
            assert not Path.home().joinpath(inst.locker_id).exists()

    @pytest.mark.parametrize(params, matrix_params)
    @pytest.mark.negative
    def test_not_found(self, crypt_id, config_arg, setup_and_teardown):
        all_lockers = list(self.lockers.keys()) + [self.locker_name]
        for lck in all_lockers:
            result = self.prep_and_run(
                config_arg, {'name': lck + "mangle"}
            )
            assert result
            assert result.exit_code == 1
            assert isinstance(result.exception, PhibesCliNotFoundError)
            # alert if tests are messing up actual user home dir
            assert not Path.home().joinpath(self.locker_name).exists()

    @pytest.mark.parametrize(params, matrix_params)
    @pytest.mark.negative
    def test_auth_fail(self, crypt_id, config_arg, setup_and_teardown):
        all_lockers = list(self.lockers.keys()) + [self.locker_name]
        for lck in all_lockers:
            result = self.prep_and_run(
                config_arg,
                {'name': lck, 'password': self.password + "mangle"}
            )
            assert result
            assert result.exit_code == 1, str(result.exception)
            assert type(result.exception) is PhibesAuthError
            # prove the locker is there if you use the right auth
            result = self.prep_and_run(
                config_arg,
                {'name': lck, 'password': self.password}
            )
            assert result
            assert result.exit_code == 0, f"{result.exception=}"
            # alert if tests are messing up actual user home dir
            assert not Path.home().joinpath(self.locker_name).exists()
