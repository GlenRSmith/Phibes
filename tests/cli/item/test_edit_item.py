"""
pytest module for phibes_cli edit (item) command
"""

# Standard library imports

# Related third party imports
import pytest
from click.testing import CliRunner

# Local application/library specific imports
from phibes import phibes_cli
from phibes.cli.lib import PhibesCliError, PhibesNotFoundError
from phibes.lib.config import set_editor, write_config_file

# Local test imports
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.locker_helper import PopulatedLocker


class TestEditBase(PopulatedLocker):

    test_item_name = 'gonna_edit'
    test_item_type = 'secret'
    good_template_name = 'good_template'
    bad_template_name = 'bad_template'
    target_cmd_name = 'edit'
    target_cmd = None

    def custom_setup(self, tmp_path):
        super(TestEditBase, self).custom_setup(tmp_path)
        my_item = self.my_locker.create_item(
            self.good_template_name, "template"
        )
        my_item.content = f"{self.good_template_name}:template"
        self.my_locker.add_item(my_item)
        set_editor("echo 'happyclappy' >> ")
        write_config_file(tmp_path, update=True)
        try:
            self.target_cmd = phibes_cli.main.commands[self.target_cmd_name]
        except KeyError:
            commands = list(phibes_cli.main.commands.keys())
            raise KeyError(
                f"{self.target_cmd_name} not found in {commands}"
            )
        update_config_option_default(self.target_cmd, tmp_path)
        return

    def custom_teardown(self, tmp_path):
        self.my_locker.delete_item(self.good_template_name, "template")
        super(TestEditBase, self).custom_teardown(tmp_path)

    def invoke(self, overwrite: bool, template: str = None):
        """
        Helper method for often repeated code in test methods
        :param overwrite:
        :param template:
        :return:
        """
        args = [
            "--locker", self.locker_name,
            "--password", self.password,
            "--item_type", self.test_item_type,
            "--item", self.test_item_name,
            "--overwrite", overwrite
        ]
        if template:
            args += ["--template", template]
        return CliRunner().invoke(self.target_cmd, args)

    def common_neg_asserts(self, result):
        assert result.exit_code == 1
        assert result.exception
        assert isinstance(result.exception, PhibesCliError)
        return

    def common_pos_asserts(self, result, expected_content):
        assert result.exit_code == 0
        inst = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        assert inst
        assert inst.content == expected_content
        return


class TestEditNew(TestEditBase):

    def custom_setup(self, tmp_path):
        super(TestEditNew, self).custom_setup(tmp_path)

    def custom_teardown(self, tmp_path):
        super(TestEditNew, self).custom_teardown(tmp_path)

    def common_neg_asserts(self, result):
        super(TestEditNew, self).common_neg_asserts(result)
        with pytest.raises(FileNotFoundError):
            self.my_locker.get_item(
                self.test_item_name, self.test_item_type
            )
        return

    def common_pos_asserts(self, result, expected_content):
        super(TestEditNew, self).common_pos_asserts(result, expected_content)
        return

    @pytest.mark.positive
    def test_notemplate(self, setup_and_teardown):
        """
        Simple case: create a new item, no template used,
        overwrite not specified
        :param setup_and_teardown: injected fixture
        :return:
        """
        result = self.invoke(False)
        self.common_pos_asserts(result, 'happyclappy\n')
        return

    @pytest.mark.negative
    def test_notemplate_overwrite(self, tmp_path, datadir, setup_and_teardown):
        """
        Conflict: naming a non-existent item but specifying overwrite
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        result = self.invoke(True)
        self.common_neg_asserts(result)
        return

    @pytest.mark.positive
    def test_goodtemplate(self, tmp_path, datadir, setup_and_teardown):
        """
        Creating a new item from an existing template
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        result = self.invoke(False, self.good_template_name)
        self.common_pos_asserts(
            result, 'good_template:templatehappyclappy\n'
        )
        return

    @pytest.mark.negative
    def test_goodtemplate_overwrite(
            self, tmp_path, datadir, setup_and_teardown
    ):
        """
        Iffy scenario, a github issue is open to discuss
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        result = self.invoke(True, self.good_template_name)
        self.common_neg_asserts(result)
        return

    @pytest.mark.negative
    def test_badtemplate(self, tmp_path, datadir, setup_and_teardown):
        """
        Template is specified that does not exist, should fail
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        result = self.invoke(False, self.bad_template_name)
        self.common_neg_asserts(result)
        return

    @pytest.mark.negative
    def test_badtemplate_overwrite(
            self, tmp_path, datadir, setup_and_teardown
    ):
        """
        Template is specified that does not exist, should fail
        Overwrite is specified, but it's a new item, should fail
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        result = self.invoke(True, self.bad_template_name)
        self.common_neg_asserts(result)
        return


class TestEditExists(TestEditBase):

    def custom_setup(self, tmp_path):
        super(TestEditExists, self).custom_setup(tmp_path)
        my_item = self.my_locker.create_item(
            self.test_item_name, self.test_item_type
        )
        my_item.content = f"{self.test_item_name}:{self.test_item_type}"
        self.my_locker.add_item(my_item)
        return

    def custom_teardown(self, tmp_path):
        super(TestEditExists, self).custom_teardown(tmp_path)

    def common_neg_asserts(self, result):
        super(TestEditExists, self).common_neg_asserts(result)
        return

    def common_pos_asserts(self, result, expected_content):
        super(TestEditExists, self).common_pos_asserts(
            result, expected_content
        )
        return

    def item_unchanged_asserts(self, before_item):
        after = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        # the item still exists and hasn't changed
        assert after is not None
        assert before_item.content == after.content
        assert before_item.timestamp == after.timestamp
        return

    @pytest.mark.negative
    def test_notemplate(self, tmp_path, datadir, setup_and_teardown):
        """
        Existing item, but overwrite isn't set True, so fail
        :param tmp_path:
        :param datadir:
        :return:
        """
        before = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        result = self.invoke(False)
        self.common_neg_asserts(result)
        self.item_unchanged_asserts(before)
        return

    @pytest.mark.positive
    def test_notemplate_overwrite(self, tmp_path, datadir, setup_and_teardown):
        """
        Specify existing item and overwrite, should succeed
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        before = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        result = self.invoke(True)
        assert result.exit_code == 0
        inst = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        assert inst
        assert 'happyclappy' in inst.content
        assert before.content in inst.content
        return

    @pytest.mark.negative
    def test_goodtemplate(self, tmp_path, datadir, setup_and_teardown):
        """
        Existing item, but overwrite isn't set True, so fail
        :param tmp_path:
        :param datadir:
        :return:
        """
        before = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        result = self.invoke(False, self.good_template_name)
        self.common_neg_asserts(result)
        assert f"{self.test_item_type}" in result.exception.message.lower()
        self.item_unchanged_asserts(before)
        return

    @pytest.mark.positive
    def test_goodtemplate_overwrite(
            self, tmp_path, datadir, setup_and_teardown
    ):
        """
        Specify existing item & template, & overwrite, should succeed
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        result = self.invoke(True, self.good_template_name)
        assert result.exit_code == 0
        inst = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        assert inst
        assert 'happyclappy' in inst.content
        assert self.good_template_name in inst.content
        return

    @pytest.mark.negative
    def test_badtemplate(self, setup_and_teardown):
        """
        Template is specified that does not exist, should fail
        Existing item without `overwrite` True, should fail
        Which error is thrown we don't care about
        :return:
        """
        before = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        result = self.invoke(False, self.bad_template_name)
        self.common_neg_asserts(result)
        self.item_unchanged_asserts(before)
        return

    @pytest.mark.negative
    def test_badtemplate_overwrite(
            self, tmp_path, datadir, setup_and_teardown
    ):
        """
        Template is specified that does not exist, should fail
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        before = self.my_locker.get_item(
            self.test_item_name, self.test_item_type
        )
        result = self.invoke(True, self.bad_template_name)
        self.common_neg_asserts(result)
        assert "template" in result.exception.message.lower()
        assert isinstance(result.exception, PhibesNotFoundError)
        self.item_unchanged_asserts(before)
        return
