"""
pytest module for phibes_cli get-item command
"""

# Standard library imports

# Related third party imports
import pytest
from click.testing import CliRunner

# Local application/library specific imports
from phibes import phibes_cli

# local test code
from tests.lib import locker_helper


class TestGetItem(locker_helper.PopulatedLocker):

    item_name = 'get_this'
    item_type = 'secret'
    missing_item_name = 'do_not_get_this'
    missing_item_type = 'tag'
    target_cmd_name = 'get-item'
    test_path = None

    def custom_setup(self, tmp_path):
        super(TestGetItem, self).custom_setup(tmp_path)
        my_item = self.my_locker.create_item(
            self.item_name, self.item_type
        )
        my_item.content = f"{self.item_type}:{self.item_name}"
        self.my_locker.add_item(my_item)
        self.list_items = phibes_cli.main.commands[self.target_cmd_name]
        return

    def custom_teardown(self, tmp_path):
        self.my_locker.delete_item(self.item_name, self.item_type)
        super(TestGetItem, self).custom_teardown(tmp_path)
        return

    def invoke(self, item_type: str, item_name: str):
        return CliRunner().invoke(
            self.list_items, [
                "--config", self.test_path,
                "--locker", self.locker_name, "--password", self.password,
                "--item_type", item_type,
                "--item", item_name
            ]
        )

    @pytest.mark.positive
    def test_get_exact_item(self, setup_and_teardown):
        result = self.invoke(self.item_type, self.item_name)
        assert result.exit_code == 0
        assert self.item_type in result.output
        assert self.item_name in result.output
        return

    @pytest.mark.positive
    def test_get_wrong_type(self, setup_and_teardown):
        result = self.invoke(self.missing_item_type, self.item_name)
        assert result.exit_code == 1
        return

    @pytest.mark.positive
    def test_get_wrong_name(self, setup_and_teardown):
        result = self.invoke(self.item_type, self.missing_item_name)
        assert result.exit_code == 1
        return

