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
from phibes.lib.config import Config
from phibes.cli.item.commands import show_item
from tests.lib import locker_helper


def copy_config(source, target):
    my_conf = source.read()
    Config.write_config(target, **json.loads(my_conf))
    return


# class ConfiguredLocker(locker_helper.PopulatedLocker):
#
#     def setup_method(self):
#         super(ConfiguredLocker, self).setup_method()
#         return
#
#     def teardown_method(self):
#         super(ConfiguredLocker, self).teardown_method()
#         return


class TestShowItem(locker_helper.PopulatedLocker):

    def _test_show_item(self, tmp_path, datadir):
        copy_config(datadir["phibes-config.json"], tmp_path)
        with capsys.disabled():
            runner = CliRunner()
            result = runner.invoke(
                show_item,
                [
                    "--locker", self.locker_name,
                    "--password", self.password,
                    "--item_type", self.delete_item_type,
                    "--item", self.delete_item_name
                ]
            )
            assert result.exit_code == 0
        return
