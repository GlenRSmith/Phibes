"""
pytest module for phibes_cli list items command
"""

# Standard library imports
# import shutil
import json

# Related third party imports
import pytest
from click.testing import CliRunner

# Local application/library specific imports
from phibes import phibes_cli
from tests.lib import locker_helper


class TestListItems(locker_helper.PopulatedLocker):

    item_name = 'list_this'
    item_type = 'secret'
    target_cmd_name = 'list'

    def setup_method(self):
        super(TestListItems, self).setup_method()
        my_item = self.my_locker.create_item(
            self.item_name, self.item_type
        )
        my_item.content = f"{self.item_type}:{self.item_name}"
        self.my_locker.add_item(my_item)
        self.list_items = phibes_cli.main.commands[self.target_cmd_name]
        return

    def invoke(self, item_type: str):
        return CliRunner().invoke(
            self.list_items, [
                "--locker", self.locker_name, "--password", self.password,
                "--item_type", self.item_type,
                "--verbose", False,
                "--item_type", item_type
            ]
        )

    def test_list_all_items(self, tmp_path, datadir):
        result = self.invoke("all")
        assert result.exit_code == 0
        for item_type in self.my_locker.registered_items.keys():
            assert item_type in result.output
        return

    def test_list_by_item_type(self, tmp_path, datadir):
        all_types = self.my_locker.registered_items.keys()
        for target_type in all_types:
            result = self.invoke(target_type)
            assert result.exit_code == 0
            assert target_type in result.output
            for inner_type in all_types:
                if inner_type != target_type:
                    assert inner_type not in result.output
        return
