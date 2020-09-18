"""
pytest module for phibes_cli create-item command
"""

# Standard library imports

# Related third party imports
import pytest
from click.testing import CliRunner

# Local application/library specific imports
from phibes import phibes_cli
from phibes.lib.errors import PhibesNotFoundError
from phibes.cli.lib import PhibesCliError, PhibesCliNotFoundError
from phibes.lib.config import set_editor, write_config_file

# Local test imports
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.locker_helper import PopulatedLocker


class TestCreateBase(PopulatedLocker):

    test_item_name = 'gonna_edit'
    test_item_type = 'secret'
    good_template_name = 'good_template'
    bad_template_name = 'bad_template'
    target_cmd_name = 'create-item'
    target_cmd = None

    def custom_setup(self, tmp_path):
        super(TestCreateBase, self).custom_setup(tmp_path)
        my_item = self.my_locker.create_item(
            self.good_template_name, "secret"
        )
        my_item.content = f"{self.good_template_name}:secret"
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
        self.my_locker.delete_item(self.good_template_name, "secret")
        super(TestCreateBase, self).custom_teardown(tmp_path)

    def invoke(self, template: str = None):
        """
        Helper method for often repeated code in test methods
        :param template:
        :return:
        """
        args = [
            "--locker", self.locker_name,
            "--password", self.password,
            "--item_type", self.test_item_type,
            "--item", self.test_item_name
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


class TestCreateNew(TestCreateBase):

    def custom_setup(self, tmp_path):
        super(TestCreateNew, self).custom_setup(tmp_path)

    def custom_teardown(self, tmp_path):
        super(TestCreateNew, self).custom_teardown(tmp_path)

    def common_neg_asserts(self, result):
        super(TestCreateNew, self).common_neg_asserts(result)
        with pytest.raises(PhibesNotFoundError):
            self.my_locker.get_item(
                self.test_item_name, self.test_item_type
            )
        return

    def common_pos_asserts(self, result, expected_content):
        super(TestCreateNew, self).common_pos_asserts(result, expected_content)
        return

    @pytest.mark.positive
    def test_notemplate(self, setup_and_teardown):
        """
        Simple case: create a new item, no template used
        :param setup_and_teardown: injected fixture
        :return:
        """
        result = self.invoke()
        self.common_pos_asserts(result, 'happyclappy\n')
        return

    @pytest.mark.positive
    def test_goodtemplate(self, tmp_path, datadir, setup_and_teardown):
        """
        Creating a new item from an existing template
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        result = self.invoke(self.good_template_name)
        self.common_pos_asserts(
            result, 'good_template:secrethappyclappy\n'
        )
        return

    @pytest.mark.negative
    def test_badtemplate(self, tmp_path, datadir, setup_and_teardown):
        """
        Template is specified that does not exist, should fail
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        result = self.invoke(self.bad_template_name)
        self.common_neg_asserts(result)
        return
