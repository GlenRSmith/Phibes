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
from phibes.cli.lib import PhibesCliNotFoundError
from phibes.lib.config import ConfigModel
from phibes.lib.errors import PhibesAuthError
from phibes.model import Locker, LOCKER_FILE
from phibes.phibes_cli import main

# Local test imports
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import PopulatedLocker


params = "command_instance,config_arg"
command_instances = [main.commands['info']]
include_config_arg = [False, True]
matrix_params = []
for element in itertools.product(command_instances, include_config_arg):
    matrix_params.append(element)


class TestAllCryptTypes(PopulatedLocker):

    def custom_setup(self, tmp_path):
        super(TestAllCryptTypes, self).custom_setup(tmp_path)

    def custom_teardown(self, tmp_path):
        super(TestAllCryptTypes, self).custom_teardown(tmp_path)

    @pytest.mark.positive
    def test_good(self, tmp_path):
        for name in self.lockers.keys():
            inst = Locker.get(password=self.password, locker_name=name)
            assert inst


class TestMatrixHashed(PopulatedLocker):

    def custom_setup(self, tmp_path):
        super(TestMatrixHashed, self).custom_setup(tmp_path)

    def custom_teardown(self, tmp_path):
        super(TestMatrixHashed, self).custom_teardown(tmp_path)

    def prep_and_run(
            self,
            config_arg,
            cmd_inst,
            arg_dict
    ):
        if config_arg:
            arg_list = ["--config", self.test_path]
        else:
            arg_list = []
        # change the configured working path to the test directory
        update_config_option_default(cmd_inst, self.test_path)
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
            cli=cmd_inst, args=arg_list
        )
        return ret_val

    @pytest.mark.parametrize(params, matrix_params)
    @pytest.mark.positive
    def test_found(self, command_instance, config_arg, setup_and_teardown):
        all_lockers = list(self.lockers.keys()) + [self.locker_name]
        for lck in all_lockers:
            result = self.prep_and_run(
                config_arg, command_instance, {'name': lck}
            )
            assert result
            assert result.exit_code == 0, (
                f"{config_arg=}\n"
                f"{command_instance=}\n"
                f"{command_instance.params=}\n"
                f"{result.exception=}\n"
                f"{result.output=}\n"
            )
            inst = Locker.get(password=self.password, locker_name=lck)
            stored_name = Locker.get_stored_name(lck)
            targ = self.test_path/stored_name/LOCKER_FILE
            assert inst.lock_file == targ
            # alert if tests are messing up actual user home dir
            assert not Path.home().joinpath(self.locker_name).exists()
            assert not Path.home().joinpath(stored_name).exists()
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
                {'name': lck + "mangle"}
            )
            assert result
            assert result.exit_code == 1
            assert isinstance(result.exception, PhibesCliNotFoundError)
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
                {'name': lck, 'password': self.password + "mangle"}
            )
            assert result
            assert result.exit_code == 1, str(result.exception)
            assert type(result.exception) is PhibesAuthError
            # prove the locker is there if you use the right auth
            result = self.prep_and_run(
                config_arg,
                command_instance,
                {'name': lck, 'password': self.password}
            )
            assert result
            assert result.exit_code == 0, f"{result.exception=}"
            # alert if tests are messing up actual user home dir
            assert not Path.home().joinpath(self.locker_name).exists()
        return
