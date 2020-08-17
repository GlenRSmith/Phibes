"""
pytest module for phibes_cli locker commands
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


class TestDeleteItem(locker_helper.PopulatedLocker):

    delete_item_name = 'gonna_delete'
    delete_item_type = 'secret'
    target_cmd_name = 'delete'

    def setup_method(self):
        super(TestDeleteItem, self).setup_method()
        my_item = self.my_locker.create_item(
            self.delete_item_name, self.delete_item_type
        )
        my_item.content = f"{self.delete_item_type}:{self.delete_item_name}"
        self.my_locker.add_item(my_item)
        self.target_cmd = phibes_cli.main.commands[self.target_cmd_name]
        return

    def invoke(self, item_type, item_name):
        """
        Helper method for often repeated code in test methods
        :param item_type:
        :param item_name:
        :return:
        """
        return CliRunner().invoke(
            self.target_cmd,
            [
                "--locker", self.locker_name,
                "--password", self.password,
                "--item_type", item_type,
                "--item", item_name
            ]
        )

    @pytest.mark.positive
    def test_delete_item(self, tmp_path, datadir):
        result = self.invoke(self.delete_item_type, self.delete_item_name)
        assert result.exit_code == 0
        # assert "deleted" in result.output
        return
