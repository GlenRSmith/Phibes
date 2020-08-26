"""
pytest module for phibes_cli locker commands
"""

# Standard library imports

# Related third party imports
import pytest
from click.testing import CliRunner

# Local application/library specific imports
from phibes import phibes_cli

# Local test imports
from tests.lib.locker_helper import PopulatedLocker


class TestDeleteItem(PopulatedLocker):

    delete_item_name = 'gonna_delete'
    delete_item_type = 'secret'
    target_cmd_name = 'delete-item'

    def custom_setup(self, tmp_path):
        super(TestDeleteItem, self).custom_setup(tmp_path)
        my_item = self.my_locker.create_item(
            self.delete_item_name, self.delete_item_type
        )
        my_item.content = f"{self.delete_item_type}:{self.delete_item_name}"
        self.my_locker.add_item(my_item)
        self.target_cmd = phibes_cli.main.commands[self.target_cmd_name]
        return

    def custom_teardown(self, tmp_path):
        super(TestDeleteItem, self).custom_teardown(tmp_path)
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
                "--config", self.test_path,
                "--locker", self.locker_name,
                "--password", self.password,
                "--item_type", item_type,
                "--item", item_name
            ]
        )

    @pytest.mark.positive
    def test_delete_item(self, setup_and_teardown):
        inst = self.my_locker.get_item(
            self.delete_item_name, self.delete_item_type
        )
        assert inst
        assert inst.name == self.delete_item_name
        result = self.invoke(self.delete_item_type, self.delete_item_name)
        assert result.exit_code == 0
        with pytest.raises(FileNotFoundError):
            self.my_locker.get_item(
                self.delete_item_name, self.delete_item_type
            )
        return
