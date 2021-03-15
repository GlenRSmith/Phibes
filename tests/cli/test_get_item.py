"""
pytest module for phibes_cli get-item command
"""

# Standard library imports

# Related third party imports
import pytest
from click.testing import CliRunner

# Local application/library specific imports
from phibes import phibes_cli
from phibes.cli.commands import Action, Target
from phibes.cli import handlers
from phibes.cli.lib import main as main_anon
from phibes.crypto import list_crypts
from phibes.cli.lib import PhibesCliNotFoundError
from phibes.lib.config import ConfigModel
from phibes.model import Locker

# local test code
from tests.lib import test_helpers
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import BaseAnonLockerTest


class TestNoName(BaseAnonLockerTest):

    password = "78CollECtion!CampCoolio"
    command_name = 'test_get_item'
    target = Target.Item
    action = Action.Get
    func = handlers.get_item
    click_group = main_anon
    test_item_name = 'gonna_getcha'
    test_content = f"here is some stuff\npassword: HardHat\nsome name\n"

    def custom_setup(self, tmp_path):
        super(TestNoName, self).custom_setup(tmp_path)

    def custom_teardown(self, tmp_path):
        super(TestNoName, self).custom_teardown(tmp_path)

    def invoke(self, arg_dict: dict):
        """
        Helper method for often repeated code in test methods
        :return: click test-runner result
        """
        args = [
            "--password", arg_dict.get('password', self.password),
            "--path", arg_dict.get('path', self.test_path),
            "--item", arg_dict.get('item', self.test_item_name)
        ]
        return CliRunner().invoke(
            self.click_group.commands[self.command_name], args
        )

    def prep_and_run(self, arg_dict):
        self.my_locker = Locker.create(
            password=self.password, crypt_id=arg_dict['crypt_id']
        )
        new_item = self.my_locker.create_item(item_name=self.test_item_name)
        new_item.content = self.test_content
        self.my_locker.add_item(item=new_item)
        # change the configured working path to the test directory
        update_config_option_default(
            self.click_group.commands[self.command_name], self.test_path
        )
        return self.invoke(arg_dict=arg_dict)

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
        assert self.test_content in result.output


class TestGetItem(test_helpers.PopulatedLocker):

    item_name = 'get_this'
    missing_item_name = 'do_not_get_this'
    target_cmd_name = 'get-item'
    test_path = None

    def custom_setup(self, tmp_path):
        super(TestGetItem, self).custom_setup(tmp_path)
        my_item = self.my_locker.create_item(self.item_name)
        my_item.content = f"{self.item_name}"
        self.my_locker.add_item(my_item)
        self.list_items = phibes_cli.main.commands[self.target_cmd_name]
        return

    def custom_teardown(self, tmp_path):
        self.my_locker.delete_item(self.item_name)
        super(TestGetItem, self).custom_teardown(tmp_path)
        return

    def invoke(self, item_name: str):
        # change the configured working path to the test directory
        update_config_option_default(self.list_items, self.test_path)
        # get the current config
        config = ConfigModel()
        # persist the changed config
        self.update_config(config)
        return CliRunner().invoke(
            catch_exceptions=False,
            cli=self.list_items,
            args=[
                "--config", self.test_path,
                "--password", self.password,
                "--locker", self.locker_name,
                "--item", item_name
            ]
        )

    @pytest.mark.positive
    def test_get_exact_item(self, setup_and_teardown, tmp_path):
        result = self.invoke(self.item_name)
        err_report = (
            f"{result=}\n"
            f"{result.exception=}\n"
            f"{result.output=}\n"
            f"{result.exit_code=}\n"
            f"{self.test_path=}\n"
        )
        assert result.exit_code == 0, err_report
        assert self.item_name in result.output

    @pytest.mark.positive
    def test_get_wrong_name(self, setup_and_teardown):
        with pytest.raises(PhibesCliNotFoundError):
            self.invoke(self.missing_item_name)
