"""
pytest module for phibes_cli list items command
"""

# Standard library imports

# Related third party imports
import pytest
from click.testing import CliRunner

# Local application/library specific imports
from phibes.cli.commands import Action, Target
from phibes.crypto import list_crypts

# local test code
from tests.lib import test_helpers
from tests.cli.click_test_helpers import GroupProvider
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import ConfigLoadingTestClass
from phibes.model import Locker


class MixinItemsList(GroupProvider):

    target = Target.Item
    action = Action.List


class TestNoName(ConfigLoadingTestClass, MixinItemsList):

    password = "78CollECtion!CampCoolio"
    test_item_name = 'gonna_getchall'
    test_content = f"here is some stuff\npassword: HardHat\nsome name\n"

    def custom_setup(self, tmp_path):
        super(TestNoName, self).custom_setup(tmp_path)
        self.setup_command()

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
        return CliRunner().invoke(cli=self.target_cmd, args=args)

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
        update_config_option_default(self.target_cmd, self.test_path)
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


class TestListItems(test_helpers.PopulatedLocker, MixinItemsList):

    item_name = 'list_this'
    test_path = None

    def custom_setup(self, tmp_path):
        super(TestListItems, self).custom_setup(tmp_path)
        my_item = self.my_locker.create_item(self.item_name)
        my_item.content = f"{self.item_name}"
        self.my_locker.add_item(my_item)
        self.setup_command()

    def custom_teardown(self, tmp_path):
        self.my_locker.delete_item(self.item_name)
        super(TestListItems, self).custom_teardown(tmp_path)

    def invoke(self):
        return CliRunner().invoke(
            catch_exceptions=False,
            cli=self.target_cmd,
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
