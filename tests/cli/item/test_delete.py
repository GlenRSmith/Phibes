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
from phibes.lib.config import Config
from tests.lib import locker_helper


def copy_config(source, target):
    my_conf = source.read()
    Config.write_config(target, **json.loads(my_conf))
    return


class TestDeleteItem(locker_helper.PopulatedLocker):

    delete_item_name = 'gonna_delete'
    delete_item_type = 'secret'

    def setup_method(self):
        super(TestDeleteItem, self).setup_method()
        my_item = self.my_locker.create_item(
            self.delete_item_name, self.delete_item_type
        )
        my_item.content = f"{self.delete_item_type}:{self.delete_item_name}"
        self.my_locker.add_item(my_item)
        self.delete_item = phibes_cli.main.commands['delete']
        return

    def delete(self, item_type, item_name):
        return CliRunner().invoke(
            self.delete_item,
            [
                "--locker", self.locker_name,
                "--password", self.password,
                "--item_type", item_type,
                "--item_name", item_name
            ]
        )

    def test_delete_item(self, tmp_path, datadir):
        copy_config(datadir["phibes-config.json"], tmp_path)
        result = self.delete(self.delete_item_type, self.delete_item_name)
        assert result.exit_code == 0
        # assert "deleted" in result.output
        return
