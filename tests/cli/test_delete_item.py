"""
pytest module for phibes_cli delete-item command
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
from phibes.lib.errors import PhibesNotFoundError
from phibes.model import Locker

# Local test imports
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import BaseAnonLockerTest
from tests.lib.test_helpers import PopulatedLocker


class TestNoName(BaseAnonLockerTest):

    password = "78CollECtion!CampCoolio"
    command_name = 'test_delete_item'
    target = Target.Item
    action = Action.Get
    func = handlers.delete_item
    click_group = main_anon
    test_item_name = 'gonna_deletecha'
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
            self.click_group.commands[self.command_name],
            args
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
            self.click_group.commands[self.command_name],
            self.test_path
        )
        return self.invoke(arg_dict=arg_dict)

    @pytest.mark.parametrize("crypt_id", list_crypts())
    @pytest.mark.positive
    def test_success(self, crypt_id, setup_and_teardown):
        result = self.prep_and_run({'crypt_id': crypt_id})
        assert result
        assert result.exit_code == 0, (
            f"{crypt_id=}\n"
            f"{result.exception=}\n"
            f"{result.output=}\n"
        )
        with pytest.raises(PhibesNotFoundError):
            self.my_locker.get_item(self.test_item_name)


class TestDeleteItem(PopulatedLocker):

    delete_item_name = 'gonna_delete'
    target_cmd_name = 'delete-item'

    def custom_setup(self, tmp_path):
        super(TestDeleteItem, self).custom_setup(tmp_path)
        my_item = self.my_locker.create_item(self.delete_item_name)
        my_item.content = f"{self.delete_item_name}"
        self.my_locker.add_item(my_item)
        self.target_cmd = phibes_cli.main.commands[self.target_cmd_name]
        return

    def custom_teardown(self, tmp_path):
        super(TestDeleteItem, self).custom_teardown(tmp_path)
        return

    def invoke(self, item_name):
        """
        Helper method for often repeated code in test methods
        :param item_name:
        :return:
        """
        return CliRunner().invoke(
            self.target_cmd,
            [
                "--config", self.test_path,
                "--locker", self.locker_name,
                "--password", self.password,
                "--item", item_name
            ]
        )

    @pytest.mark.positive
    def test_delete_item(self, setup_and_teardown):
        inst = self.my_locker.get_item(self.delete_item_name)
        assert inst
        assert inst.name == self.delete_item_name
        result = self.invoke(self.delete_item_name)
        assert result.exit_code == 0, (
            f"      {self.locker_name=}      "
            f"      {result=}      "
        )
        with pytest.raises(PhibesNotFoundError):
            self.my_locker.get_item(self.delete_item_name)
        return
