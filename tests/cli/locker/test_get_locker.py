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
from phibes.lib.crypto import get_name_hash
from phibes.lib.errors import PhibesAuthError, PhibesNotFoundError
from phibes.lib.locker import Locker, LOCKER_FILE
from phibes.phibes_cli import main

# Local test imports
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.locker_helper import ConfigLoadingTestClass


params = "command_instance,config_arg,hash_names,change_hashing_after_create"
command_instances = [get_locker_cmd, main.commands['get-locker']]
include_config_arg = [False, True]
config_hash_locker_names = [False, True]
change_hashing_after_create = [False, True]
matrix_params = []
for element in itertools.product(
    command_instances,
    include_config_arg,
    config_hash_locker_names,
    change_hashing_after_create
):
    matrix_params.append(element)


class TestMatrix(ConfigLoadingTestClass):

    hash_locker_names = True
    name = "test_hashed_new_locker"
    pw = "SmellyBeansVictor"

    def custom_setup(self, tmp_path):
        super(TestMatrix, self).custom_setup(tmp_path)
        try:
            Locker.delete(self.name, self.pw)
        except PhibesNotFoundError:
            pass
        Locker(self.name, self.pw, create=True)
        return

    def custom_teardown(self, tmp_path):
        super(TestMatrix, self).custom_teardown(tmp_path)
        try:
            Locker.delete(self.name, self.pw)
        except PhibesNotFoundError:
            pass
        return

    def prep_and_run(
            self, config_arg, cmd_inst, hash_names, arg_dict, chg_hash
    ):
        inst = Locker(self.name, self.pw)
        assert inst
        if config_arg:
            arg_list = ["--config", self.test_path]
        else:
            update_config_option_default(cmd_inst, self.test_path)
            config = ConfigModel()
            config.hash_locker_names = hash_names
            self.update_config(config)
            arg_list = []
        arg_list += [
            "--locker", arg_dict.get('name', self.name),
            "--password", arg_dict.get('password', self.pw)
        ]
        if chg_hash:
            conf = ConfigModel()
            conf.hash_locker_names = not conf.hash_locker_names
            self.update_config(conf)
        return CliRunner().invoke(cmd_inst, arg_list)

    @pytest.mark.parametrize(params, matrix_params)
    @pytest.mark.positive
    def test_found(
            self,
            command_instance,
            config_arg,
            hash_names,
            change_hashing_after_create,
            setup_and_teardown
    ):
        result = self.prep_and_run(
            config_arg,
            command_instance,
            hash_names,
            {},
            change_hashing_after_create
        )
        assert result
        assert result.exit_code == 0
        targ = self.test_path/get_name_hash(self.name)/LOCKER_FILE
        inst = Locker(self.name, self.pw)
        assert inst.lock_file == targ
        # alert if tests are messing up actual user home dir
        assert not Path.home().joinpath(self.name).exists()
        assert not Path.home().joinpath(get_name_hash(self.name)).exists()
        return

    @pytest.mark.parametrize(params, matrix_params)
    @pytest.mark.negative
    def test_not_found(
            self,
            command_instance,
            config_arg,
            hash_names,
            change_hashing_after_create,
            setup_and_teardown
    ):
        result = self.prep_and_run(
            config_arg,
            command_instance,
            hash_names,
            {'name': self.name + "mangle"},
            change_hashing_after_create
        )
        assert result
        assert result.exit_code == 1
        assert type(result.exception) is PhibesCliNotFoundError
        # alert if tests are messing up actual user home dir
        assert not Path.home().joinpath(self.name).exists()
        assert not Path.home().joinpath(get_name_hash(self.name)).exists()
        return

    @pytest.mark.parametrize(params, matrix_params)
    @pytest.mark.negative
    def test_auth_fail(
            self,
            command_instance,
            config_arg,
            hash_names,
            change_hashing_after_create,
            setup_and_teardown
    ):
        result = self.prep_and_run(
            config_arg,
            command_instance,
            hash_names,
            {'password': self.pw + "mangle"},
            change_hashing_after_create
        )
        assert result
        assert result.exit_code == 1
        assert type(result.exception) is PhibesAuthError
        # prove the locker is there if you use the right auth
        result = self.prep_and_run(
            config_arg,
            command_instance,
            hash_names,
            {},
            change_hashing_after_create
        )
        assert result
        assert result.exit_code == 0
        # alert if tests are messing up actual user home dir
        assert not Path.home().joinpath(self.name).exists()
        assert not Path.home().joinpath(get_name_hash(self.name)).exists()
        return
