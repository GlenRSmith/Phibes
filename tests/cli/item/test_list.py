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
from phibes.lib.config import Config
from tests.lib import locker_helper


def copy_config(source, target):
    my_conf = source.read()
    Config.write_config(target, **json.loads(my_conf))
    return


class TestListItems(locker_helper.PopulatedLocker):

    item_name = 'list_this'
    item_type = 'secret'

    def setup_method(self):
        super(TestListItems, self).setup_method()
        my_item = self.my_locker.create_item(
            self.item_name, self.item_type
        )
        my_item.content = f"{self.item_type}:{self.item_name}"
        self.my_locker.add_item(my_item)
        self.common_args = [
            "--locker", self.locker_name, "--password", self.password,
            "--item_type", self.item_type,
            "--verbose", False,
        ]
        self.runner = CliRunner()
        self.list_items = phibes_cli.main.commands['list']
        return

    def test_list_all_items(self, tmp_path, datadir):
        copy_config(datadir["phibes-config.json"], tmp_path)
        runner = CliRunner()
        result = runner.invoke(
            self.list_items, self.common_args + ["--item_type", "all"]
        )
        assert result.exit_code == 0
        return
