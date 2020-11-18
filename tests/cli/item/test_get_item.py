"""
pytest module for phibes_cli get-item command
"""

# Standard library imports

# Related third party imports
import pytest
from click.testing import CliRunner

# Local application/library specific imports
from phibes import phibes_cli
from phibes.cli.lib import PhibesCliNotFoundError

# local test code
from tests.lib import test_helpers


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
        return CliRunner().invoke(
            self.list_items, [
                "--config", self.test_path,
                "--locker", self.locker_name, "--password", self.password,
                "--item", item_name
            ]
        )

    @pytest.mark.positive
    def test_get_exact_item(self, setup_and_teardown):
        result = self.invoke(self.item_name)
        assert result.exit_code == 0
        assert self.item_name in result.output
        return

    @pytest.mark.positive
    def test_get_wrong_name(self, setup_and_teardown):
        result = self.invoke(self.missing_item_name)
        assert result.exit_code == 1
        assert type(result.exception) is PhibesCliNotFoundError
        return

