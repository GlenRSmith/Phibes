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
from tests.lib import test_helpers


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
