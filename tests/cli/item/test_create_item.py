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
from phibes.cli.lib import PhibesCliError
from phibes.lib.config import set_editor, write_config_file

# Local test imports
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import PopulatedLocker


class TestCreateBase(PopulatedLocker):

    test_item_name = 'gonna_edit'
    test_item_type = 'secret'
    good_template_name = 'good_template'
    bad_template_name = 'bad_template'
    target_cmd_name = 'create-item'
    target_cmd = None

    def custom_setup(self, tmp_path):
        super(TestCreateBase, self).custom_setup(tmp_path)
        for name, inst in self.lockers.items():
            my_item = inst.create_item(self.good_template_name)
            my_item.content = f"{self.good_template_name}:secret"
            inst.add_item(my_item)
        my_item = self.my_locker.create_item(self.good_template_name)
        my_item.content = f"{self.good_template_name}:secret"
        self.my_locker.add_item(my_item)
        set_editor('echo happyclappy>> ')
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
        logs = ""
        self.my_locker.delete_item(self.good_template_name)
        logs += f"deleted {self.good_template_name} from {self.my_locker}\t"
        for name, inst in TestCreateBase.lockers.items():
            try:
                inst.delete_item(self.good_template_name)
                logs += f"deleted {self.good_template_name} from {name}\t"
            except FileNotFoundError as err:
                logs += f"fail: {name=} {inst=}\t"
                raise FileNotFoundError(f"{logs}\n{err}")

        super(TestCreateBase, self).custom_teardown(tmp_path)

    def invoke(self, template: str = None, locker_name: str = None):
        """
        Helper method for often repeated code in test methods
        :param template: Name of item to use as template for new item
        :param locker_name: Name of locker
        :return: click test-runner result
        """
        if locker_name is None:
            locker_name = self.locker_name
        args = [
            "--locker", (locker_name, self.locker_name)[locker_name is None],
            "--password", self.password,
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

    def common_pos_asserts(self, result, expected_content, locker_inst=None):
        assert result.exit_code == 0
        if locker_inst is None:
            locker_inst = self.my_locker
        inst = locker_inst.get_item(self.test_item_name)
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
            self.my_locker.get_item(self.test_item_name)
        return

    def common_pos_asserts(self, result, expected_content, locker_inst=None):
        super(TestCreateNew, self).common_pos_asserts(
            result, expected_content, locker_inst
        )
        return

    @pytest.mark.positive
    def test_notemplate(self, setup_and_teardown):
        """
        Simple case: create a new item, no template used
        :param setup_and_teardown: injected fixture
        :return:
        """
        for name in self.lockers.keys():
            result = self.invoke(locker_name=name)
            self.common_pos_asserts(
                result, 'happyclappy\n', self.lockers[name]
            )
        result = self.invoke()
        self.common_pos_asserts(result, 'happyclappy\n')
        return

    @pytest.mark.positive
    def test_goodtemplate(self, tmp_path, setup_and_teardown):
        """
        Creating a new item from an existing template
        :param tmp_path: pytest plugin injected
        :return:
        """
        for name in self.lockers.keys():
            result = self.invoke(self.good_template_name, locker_name=name)
            self.common_pos_asserts(
                result,
                'good_template:secrethappyclappy\n',
                self.lockers[name]
            )
        result = self.invoke(self.good_template_name)
        self.common_pos_asserts(result, 'good_template:secrethappyclappy\n')
        return

    @pytest.mark.negative
    def test_badtemplate(self, tmp_path, setup_and_teardown):
        """
        Template is specified that does not exist, should fail
        :param tmp_path: pytest plugin injected
        :return:
        """
        for name in self.lockers.keys():
            result = self.invoke(self.bad_template_name, locker_name=name)
            self.common_neg_asserts(result)
        result = self.invoke(self.bad_template_name)
        self.common_neg_asserts(result)
        return
