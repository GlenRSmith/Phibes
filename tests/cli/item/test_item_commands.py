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


class TestEditNew(locker_helper.PopulatedLocker):

    test_item_name = 'gonna_edit'
    test_item_type = 'secret'
    good_template_name = 'good_template'
    bad_template_name = 'bad_template'

    def setup_method(self):
        super(TestEditNew, self).setup_method()
        my_item = self.my_locker.create_item(
            self.good_template_name, "template"
        )
        my_item.content = f"{self.good_template_name}:template"
        self.my_locker.add_item(my_item)
        self.common_args = [
            "--locker", self.locker_name, "--password", self.password,
            "--item_type", self.test_item_type,
            "--item", self.test_item_name,
            "--editor", "echo 'happyclappy' >> "
        ]
        self.runner = CliRunner()
        return

    @pytest.mark.positive
    def test_notemplate(self, tmp_path, datadir):
        """
        Simple case: create a new item, no template used,
        overwrite not specified
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        copy_config(datadir["phibes-config.json"], tmp_path)
        result = self.runner.invoke(
            edit, self.common_args + ["--overwrite", False]
        )
        assert result.exit_code == 0
        inst = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        assert inst
        assert inst.content == 'happyclappy\n'
        return

    @pytest.mark.negative
    def test_notemplate_overwrite(self, tmp_path, datadir):
        """
        Conflict: naming a non-existent item but specifying overwrite
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        copy_config(datadir["phibes-config.json"], tmp_path)
        result = self.runner.invoke(
            edit, self.common_args + ["--overwrite", True]
        )
        assert result.exit_code == 1
        assert "Phibes" in result.output
        assert "Error" in result.output
        assert result.exception
        with pytest.raises(FileNotFoundError):
            self.my_locker.get_item(
                self.test_item_name, self.test_item_type
            )
        return

    @pytest.mark.positive
    def test_goodtemplate(self, tmp_path, datadir):
        """
        Creating a new item from an existing template
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        copy_config(datadir["phibes-config.json"], tmp_path)
        result = self.runner.invoke(
            edit, self.common_args +
                [
                  "--overwrite", False,
                  "--template", self.good_template_name
                ]
        )
        assert result.exit_code == 0
        inst = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        assert inst
        assert 'happyclappy' in inst.content
        assert self.good_template_name in inst.content
        return

    @pytest.mark.negative
    def test_goodtemplate_overwrite(self, tmp_path, datadir):
        """
        Iffy scenario, a github issue is open to discuss
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        copy_config(datadir["phibes-config.json"], tmp_path)
        result = self.runner.invoke(
            edit, self.common_args +
                  [
                      "--overwrite", True,
                      "--template", self.good_template_name
                  ]
        )
        assert result.exit_code == 1
        assert "Phibes" in result.output
        assert "Error" in result.output
        assert result.exception
        with pytest.raises(FileNotFoundError):
            self.my_locker.get_item(
                self.test_item_name, self.test_item_type
            )
        return

    @pytest.mark.negative
    def test_badtemplate(self, tmp_path, datadir):
        """
        Template is specified that does not exist, should fail
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        copy_config(datadir["phibes-config.json"], tmp_path)
        result = self.runner.invoke(
            edit, self.common_args +
                  [
                      "--overwrite", False,
                      "--template", self.bad_template_name
                  ]
        )
        assert result.exit_code == 1
        assert "Phibes" in result.output
        assert "Error" in result.output
        assert result.exception
        with pytest.raises(FileNotFoundError):
            self.my_locker.get_item(
                self.test_item_name, self.test_item_type
            )
        return

    @pytest.mark.negative
    def test_badtemplate_overwrite(self, tmp_path, datadir):
        """
        Template is specified that does not exist, should fail
        Overwrite is specified, but it's a new item, should fail
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        copy_config(datadir["phibes-config.json"], tmp_path)
        result = self.runner.invoke(
            edit, self.common_args +
                  [
                      "--overwrite", True,
                      "--template", self.bad_template_name
                  ]
        )
        assert result.exit_code == 1
        assert "Phibes" in result.output
        assert "Error" in result.output
        assert result.exception
        with pytest.raises(FileNotFoundError):
            self.my_locker.get_item(
                self.test_item_name, self.test_item_type
            )
        return


class TestEditExists(locker_helper.PopulatedLocker):

    test_item_name = 'gonna_edit'
    test_item_type = 'secret'
    good_template_name = 'good_template'
    bad_template_name = 'bad_template'

    def dry_bad_assertions(self, result):
        assert result.exit_code == 1
        assert "Phibes" in result.output
        assert "Error" in result.output
        assert "template" in result.output
        assert result.exception

    def setup_method(self):
        super(TestEditExists, self).setup_method()
        my_item = self.my_locker.create_item(
            self.test_item_name, self.test_item_type
        )
        my_item.content = f"{self.test_item_name}:{self.test_item_type}"
        self.my_locker.add_item(my_item)
        my_item = self.my_locker.create_item(
            self.good_template_name, "template"
        )
        my_item.content = f"{self.good_template_name}:template"
        self.my_locker.add_item(my_item)
        self.common_args = [
            "--locker", self.locker_name, "--password", self.password,
            "--item_type", self.test_item_type,
            "--item", self.test_item_name,
            "--editor", "echo 'happyclappy' >> "
        ]
        self.runner = CliRunner()
        return

    @pytest.mark.negative
    def test_notemplate(self, tmp_path, datadir):
        """
        Existing item, but overwrite isn't set True, so fail
        :param tmp_path:
        :param datadir:
        :return:
        """
        copy_config(datadir["phibes-config.json"], tmp_path)
        before = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        result = self.runner.invoke(
            edit, self.common_args + ["--overwrite", False]
        )
        assert result.exit_code == 1
        assert "Phibes" in result.output
        assert "Error" in result.output
        assert "template" in result.output
        assert result.exception
        after = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        # the item still exists and hasn't changed
        assert after is not None
        assert before.content == after.content
        assert before.timestamp == after.timestamp
        return

    @pytest.mark.positive
    def test_notemplate_overwrite(self, tmp_path, datadir):
        """
        Specify existing item and overwrite, should succeed
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        copy_config(datadir["phibes-config.json"], tmp_path)
        before = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        result = self.runner.invoke(
            edit, self.common_args + ["--overwrite", True]
        )
        assert result.exit_code == 0
        inst = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        assert inst
        assert 'happyclappy' in inst.content
        assert before.content in inst.content
        return

    @pytest.mark.negative
    def test_goodtemplate(self, tmp_path, datadir):
        """
        Existing item, but overwrite isn't set True, so fail
        :param tmp_path:
        :param datadir:
        :return:
        """
        copy_config(datadir["phibes-config.json"], tmp_path)
        before = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        result = self.runner.invoke(
            edit, self.common_args + [
                "--overwrite", False,
                "--template", self.good_template_name
            ]
        )
        assert result.exit_code == 1
        assert "Phibes" in result.output
        assert "Error" in result.output
        assert f"{self.test_item_type}" in result.output
        assert result.exception
        after = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        # the item still exists and hasn't changed
        assert after is not None
        assert before.content == after.content
        assert before.timestamp == after.timestamp
        return

    @pytest.mark.positive
    def test_goodtemplate_overwrite(self, tmp_path, datadir):
        """
        Specify existing item & template, & overwrite, should succeed
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        copy_config(datadir["phibes-config.json"], tmp_path)
        result = self.runner.invoke(
            edit, self.common_args +
                [
                  "--overwrite", True,
                  "--template", self.good_template_name
                ]
        )
        assert result.exit_code == 0
        inst = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        assert inst
        assert 'happyclappy' in inst.content
        assert self.good_template_name in inst.content
        return

    @pytest.mark.negative
    def test_badtemplate(self, tmp_path, datadir):
        """
        Template is specified that does not exist, should fail
        Existing item without `overwrite` True, should fail
        Which error is thrown we don't care about
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        copy_config(datadir["phibes-config.json"], tmp_path)
        before = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        result = self.runner.invoke(
            edit, self.common_args + [
                "--overwrite", False,
                "--template", self.bad_template_name
            ]
        )
        assert result.exit_code == 1
        assert "Phibes" in result.output
        assert "Error" in result.output
        assert result.exception
        after = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        # the item still exists and hasn't changed
        assert after is not None
        assert before.content == after.content
        assert before.timestamp == after.timestamp
        return

    @pytest.mark.negative
    def test_badtemplate_overwrite(self, tmp_path, datadir):
        """
        Template is specified that does not exist, should fail
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        copy_config(datadir["phibes-config.json"], tmp_path)
        before = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        result = self.runner.invoke(
            edit, self.common_args + [
                "--overwrite", True,
                "--template", self.bad_template_name
            ]
        )
        assert result.exit_code == 1
        assert "Phibes" in result.output
        assert "Error" in result.output
        assert "template" in result.output
        assert result.exception
        after = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        # the item still exists and hasn't changed
        assert after is not None
        assert before.content == after.content
        assert before.timestamp == after.timestamp
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

    def _test_delete_item(self, tmp_path, datadir):
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


class TestListItems(locker_helper.PopulatedLocker):

    def _test_list_items(self, tmp_path, datadir):
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

    def _test_ls(self, tmp_path, datadir):
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
