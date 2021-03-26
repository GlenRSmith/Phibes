"""
pytest module for phibes_cli list items command
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

# local test code
from tests.lib import test_helpers
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import BaseAnonLockerTest
from phibes.model import Locker


class TestNoName(BaseAnonLockerTest):

    password = "78CollECtion!CampCoolio"
    command_name = 'test_list_items'
    target = Target.Item
    action = Action.List
    func = handlers.get_items
    click_group = main_anon
    test_item_name = 'gonna_getchall'
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
            "--verbose", True
        ]
        return CliRunner().invoke(
            cli=self.click_group.commands[self.command_name],
            args=args
        )

    def prep_and_run(self, arg_dict):
        self.my_locker = Locker.create(
            password=self.password,
            crypt_id=arg_dict['crypt_id']
        )
        new_item = self.my_locker.create_item(
            item_name=self.test_item_name
        )
        new_item.content = self.test_content
        self.my_locker.add_item(item=new_item)
        update_config_option_default(
            self.click_group.commands[self.command_name],
            self.test_path
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
        for part in [self.test_content, self.test_item_name]:
            assert part in result.output, (
                f"{crypt_id=}\n"
                f"{result.exception=}\n"
                f"{result.output=}\n"
            )


class TestListItems(test_helpers.PopulatedLocker):

    item_name = 'list_this'
    target_cmd_name = 'list'
    test_path = None

    def custom_setup(self, tmp_path):
        super(TestListItems, self).custom_setup(tmp_path)
        my_item = self.my_locker.create_item(self.item_name)
        my_item.content = f"{self.item_name}"
        self.my_locker.add_item(my_item)
        self.list_items = phibes_cli.main.commands[self.target_cmd_name]
        return

    def custom_teardown(self, tmp_path):
        self.my_locker.delete_item(self.item_name)
        super(TestListItems, self).custom_teardown(tmp_path)
        return

    def invoke(self):
        return CliRunner().invoke(
            catch_exceptions=False,
            cli=self.list_items,
            args=[
                "--config", self.test_path,
                "--locker", self.locker_name,
                "--password", self.password,
                "--verbose", False
            ]
        )

    @pytest.mark.positive
    def test_list_all_items(self, setup_and_teardown):
        result = self.invoke()
        assert result.exit_code == 0, result.output
        return
