"""
pytest module for phibes_cli list items command
"""

# Standard library imports

# Related third party imports
import pytest
from click.testing import CliRunner

# Local application/library specific imports
from phibes import phibes_cli

# local test code
from tests.lib import locker_helper


class TestListItems(locker_helper.PopulatedLocker):

    item_name = 'list_this'
    item_type = 'secret'
    target_cmd_name = 'list'
    test_path = None

    def custom_setup(self, tmp_path):
        super(TestListItems, self).custom_setup(tmp_path)
        my_item = self.my_locker.create_item(
            self.item_name, self.item_type
        )
        my_item.content = f"{self.item_type}:{self.item_name}"
        self.my_locker.add_item(my_item)
        self.list_items = phibes_cli.main.commands[self.target_cmd_name]
        return

    def custom_teardown(self, tmp_path):
        self.my_locker.delete_item(self.item_name, self.item_type)
        super(TestListItems, self).custom_teardown(tmp_path)
        return

    def invoke(self, item_type: str):
        return CliRunner().invoke(
            self.list_items, [
                "--config", self.test_path,
                "--locker", self.locker_name, "--password", self.password,
                "--verbose", False,
                "--item_type", item_type
            ]
        )

    @pytest.mark.positive
    def test_list_all_items(self, setup_and_teardown):
        result = self.invoke("all")
        assert result.exit_code == 0
        for item_type in self.my_locker.registered_items.keys():
            assert item_type in result.output
        return

    @pytest.mark.positive
    def test_list_by_item_type(self, setup_and_teardown):
        all_types = self.my_locker.registered_items.keys()
        for target_type in all_types:
            result = self.invoke(target_type)
            assert result.exit_code == 0
            assert target_type in result.output
            for inner_type in all_types:
                if inner_type != target_type:
                    assert inner_type not in result.output
        return
