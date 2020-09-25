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
from phibes.cli.locker.get import get_locker_cmd
from phibes.cli.lib import PhibesCliNotFoundError
from phibes.lib.config import ConfigModel
from phibes.lib.errors import PhibesAuthError, PhibesConfigurationError
from phibes.model import Locker, LOCKER_FILE
from phibes.phibes_cli import main

# Local test imports
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.locker_helper import PopulatedLocker


params = "command_instance,config_arg"
command_instances = [get_locker_cmd, main.commands['get-locker']]
include_config_arg = [False, True]
matrix_params = []
for element in itertools.product(command_instances, include_config_arg):
    matrix_params.append(element)


class TestAllCryptTypes(PopulatedLocker):

    def custom_setup(self, tmp_path):
        super(TestAllCryptTypes, self).custom_setup(tmp_path)

    def custom_teardown(self, tmp_path):
        super(TestAllCryptTypes, self).custom_teardown(tmp_path)

    def test_good(self, tmp_path):
        for name in self.lockers.keys():
            inst = Locker.get(name, self.password)
            assert inst


class TestMatrixHashed(PopulatedLocker):

    hash_locker_names = True

    def custom_setup(self, tmp_path):
        super(TestMatrixHashed, self).custom_setup(tmp_path)

    def custom_teardown(self, tmp_path):
        super(TestMatrixHashed, self).custom_teardown(tmp_path)

    def prep_and_run(
            self,
            config_arg,
            cmd_inst,
            arg_dict,
            chg_hash
    ):
        if config_arg:
            arg_list = ["--config", self.test_path]
        else:
            # change the configured working path to the test directory
            update_config_option_default(cmd_inst, self.test_path)
            # get the current config
            config = ConfigModel()
            # update it with the setting for this test
            config.hash_locker_names = self.hash_locker_names
            # persist the changed config
            self.update_config(config)
            arg_list = []
        arg_list += [
            "--locker", arg_dict.get('name', self.locker_name),
            "--password", arg_dict.get('password', self.password)
        ]
        if chg_hash:
            conf = ConfigModel()
            conf.hash_locker_names = not conf.hash_locker_names
            self.update_config(conf)
        ret_val = CliRunner().invoke(cmd_inst, arg_list)
        return ret_val

    @pytest.mark.parametrize(params, matrix_params)
    @pytest.mark.positive
    def test_found(self, command_instance, config_arg, setup_and_teardown):
        all_lockers = list(self.lockers.keys()) + [self.locker_name]
        for lck in all_lockers:
            result = self.prep_and_run(
                config_arg, command_instance, {'name': lck}, chg_hash=False
            )
            assert result
            print(f"{result}")
            assert result.exit_code == 0
            inst = Locker.get(lck, self.password)
            hash_dir = inst.crypt_impl.hash_name(self.locker_name)
            targ = self.test_path/hash_dir/LOCKER_FILE
            assert inst.lock_file == targ
            # alert if tests are messing up actual user home dir
            assert not Path.home().joinpath(self.locker_name).exists()
            assert not Path.home().joinpath(hash_dir).exists()
            return

    @pytest.mark.parametrize(params, matrix_params)
    @pytest.mark.negative
    def test_not_found(
            self,
            command_instance,
            config_arg,
            setup_and_teardown
    ):
        all_lockers = list(self.lockers.keys()) + [self.locker_name]
        for lck in all_lockers:
            result = self.prep_and_run(
                config_arg,
                command_instance,
                {'name': lck + "mangle"},
                chg_hash=False
            )
            assert result
            assert result.exit_code == 1
            assert type(result.exception) is PhibesCliNotFoundError
            # alert if tests are messing up actual user home dir
            assert not Path.home().joinpath(self.locker_name).exists()
        return

    @pytest.mark.parametrize(params, matrix_params)
    @pytest.mark.negative
    def test_auth_fail(self, command_instance, config_arg, setup_and_teardown):
        all_lockers = list(self.lockers.keys()) + [self.locker_name]
        for lck in all_lockers:
            result = self.prep_and_run(
                config_arg,
                command_instance,
                {'name': lck, 'password': self.password + "mangle"},
                chg_hash=False
            )
            assert result
            assert result.exit_code == 1
            assert type(result.exception) is PhibesAuthError
            # prove the locker is there if you use the right auth
            result = self.prep_and_run(
                config_arg,
                command_instance,
                {'name': lck, 'password': self.password},
                chg_hash=False
            )
            assert result
            assert result.exit_code == 0
            # alert if tests are messing up actual user home dir
            assert not Path.home().joinpath(self.locker_name).exists()
        return

    @pytest.mark.parametrize(params, matrix_params)
    @pytest.mark.negative
    def test_conf_hash_issue(
            self, command_instance, config_arg, setup_and_teardown
    ):
        all_lockers = list(self.lockers.keys()) + [self.locker_name]
        for lck in all_lockers:
            result = self.prep_and_run(
                config_arg,
                command_instance,
                {'name': lck, 'password': self.password},
                chg_hash=True
            )
            assert result
            assert result.exit_code == 1
            assert type(result.exception) is PhibesConfigurationError
            # alert if tests are messing up actual user home dir
            assert not Path.home().joinpath(self.locker_name).exists()
        return


class TestMatrixUnHashed(TestMatrixHashed):

    hash_locker_names = False

    @pytest.mark.parametrize(params, matrix_params)
    @pytest.mark.positive
    def test_found(self, command_instance, config_arg, setup_and_teardown):
        result = self.prep_and_run(
            config_arg, command_instance, {}, chg_hash=False
        )
        assert result
        assert result.exit_code == 0
        targ = self.test_path/self.locker_name/LOCKER_FILE
        inst = Locker.get(self.locker_name, self.password)
        assert inst.lock_file == targ
        # alert if tests are messing up actual user home dir
        assert not Path.home().joinpath(self.locker_name).exists()
        return
