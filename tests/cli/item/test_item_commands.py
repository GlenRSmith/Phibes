"""
pytest module for phibes_cli locker commands
"""

# Standard library imports
# import shutil
import json

# Related third party imports
from click.testing import CliRunner

# Local application/library specific imports
from phibes.lib.config import Config
from phibes.lib.item import Item
from phibes.lib.locker import Locker
from phibes.cli.item.commands import delete_item, edit
from phibes.cli.item.commands import list_items, ls, show_item
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


class TestEdit(locker_helper.PopulatedLocker):

    test_item_name = 'gonna_edit'
    test_item_type = 'secret'

    def setup_method(self):
        super(TestEdit, self).setup_method()
        my_item = self.my_locker.create_item(
            self.test_item_name, self.test_item_type
        )
        my_item.content = f"{self.test_item_name}:{self.test_item_type}"
        self.my_locker.add_item(my_item)
        return

    def test_edit(self, tmp_path, datadir, capsys):
        copy_config(datadir["phibes-config.json"], tmp_path)
        with capsys.disabled():
            runner = CliRunner()
            result = runner.invoke(
                edit,
                [
                    "--locker", self.locker_name,
                    "--password", self.password,
                    "--item_type", self.test_item_type,
                    "--item", self.test_item_name,
                    "--editor", "echo 'happyclappy' > ",
                    "--overwrite", True
                ]
            )
            assert result.exit_code == 0
        inst = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        assert inst
        assert inst.content == 'happyclappy\n'
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
        return

    def _test_delete_item(self, tmp_path, datadir, capsys):
        copy_config(datadir["phibes-config.json"], tmp_path)
        with capsys.disabled():
            runner = CliRunner()
            result = runner.invoke(
                delete_item,
                [
                    "--locker", self.locker_name,
                    "--password", self.password,
                    "--item_type", self.delete_item_type,
                    "--item", self.delete_item_name
                ]
            )
            assert result.exit_code == 0
            # assert "deleted" in result.output
        return


class TestShowItem(locker_helper.PopulatedLocker):

    def _test_show_item(self, tmp_path, datadir, capsys):
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


class TestListItems(locker_helper.PopulatedLocker):

    def _test_list_items(self, tmp_path, datadir, capsys):
        copy_config(datadir["phibes-config.json"], tmp_path)
        with capsys.disabled():
            runner = CliRunner()
            result = runner.invoke(
                list_items,
                [
                    "--locker", self.locker_name,
                    "--password", self.password,
                    "--item_type", self.delete_item_type,
                    "--item", self.delete_item_name
                ]
            )
            assert result.exit_code == 0
        return


class TestLs(locker_helper.PopulatedLocker):

    def _test_ls(self, tmp_path, datadir, capsys):
        copy_config(datadir["phibes-config.json"], tmp_path)
        with capsys.disabled():
            runner = CliRunner()
            result = runner.invoke(
                ls,
                [
                    "--locker", self.locker_name,
                    "--password", self.password,
                    "--item_type", self.delete_item_type,
                    "--item", self.delete_item_name
                ]
            )
            assert result.exit_code == 0
        return
