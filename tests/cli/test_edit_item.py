"""
pytest module for phibes_cli edit (item) command
"""

# Standard library imports
# Related third party imports
from click.testing import CliRunner
import pytest

# Local application/library specific imports
from phibes.cli import PhibesCliError
from phibes.cli.cli_config import CliConfig, load_config_file, write_config_file
from phibes.cli.commands import Action, Target
from phibes.crypto import list_crypts
from phibes.lib.errors import PhibesNotFoundError
from phibes.model import Locker

# Local test imports
from tests.cli.click_test_helpers import GroupProvider
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import ConfigLoadingTestClass
from tests.lib.test_helpers import PopulatedLocker


class MixinItemEdit(GroupProvider):

    target = Target.Item
    action = Action.Update


class TestNoName(ConfigLoadingTestClass, MixinItemEdit):

    password = "78CollECtion!CampCoolio"
    test_item_name = 'gonna_editecha'
    start_content = f"replace this\n"
    edit_content = f"unique"

    def custom_setup(self, tmp_path):
        super(TestNoName, self).custom_setup(tmp_path)
        self.setup_command()

    def custom_teardown(self, tmp_path):
        super(TestNoName, self).custom_teardown(tmp_path)

    def invoke(self, arg_dict: dict):
        """
        Helper method for often repeated code in test methods
        :return: click test-runner result
        """
        args = [
            "--password", arg_dict.get('password', self.password),
            "--path", arg_dict.get('path', self.test_path),
            "--item", arg_dict.get('item', self.test_item_name)
        ]
        return CliRunner().invoke(self.target_cmd, args)

    def prep_and_run(self, arg_dict):
        return self.invoke(arg_dict=arg_dict)

    @pytest.mark.parametrize("crypt_id", list_crypts())
    @pytest.mark.positive
    def test_success(self, crypt_id, tmp_path, setup_and_teardown):
        self.my_locker = Locker.create(
            password=self.password, crypt_id=crypt_id
        )
        new_item = self.my_locker.create_item(item_name=self.test_item_name)
        new_item.content = self.start_content
        self.my_locker.add_item(item=new_item)
        conf = CliConfig()
        conf.store = {
            'store_type': conf.store['store_type'],
            'store_path': tmp_path
        }
        conf.editor = f'echo {self.edit_content}> '
        write_config_file(tmp_path, update=True)
        load_config_file(tmp_path)
        # change the configured working path to the test directory
        update_config_option_default(self.target_cmd, self.test_path)
        result = self.prep_and_run({'crypt_id': crypt_id})
        assert result
        assert result.exit_code == 0, (
            f"{crypt_id=}\n"
            f"{result.exception=}\n"
            f"{result.output=}\n"
        )
        assert self.start_content not in result.output
        inst = self.my_locker.get_item(self.test_item_name)
        assert self.edit_content == inst.content.strip()


class TestEditBase(PopulatedLocker, MixinItemEdit):

    test_item_name = 'gonna_edit'
    good_template_name = 'good_template'
    bad_template_name = 'bad_template'

    def custom_setup(self, tmp_path):
        super(TestEditBase, self).custom_setup(tmp_path)
        my_item = self.my_locker.create_item(self.good_template_name)
        my_item.content = f"{self.good_template_name}:secret"
        self.my_locker.add_item(my_item)
        CliConfig().editor = "echo 'happyclappy' >> "
        write_config_file(tmp_path, update=True)
        self.setup_command()
        update_config_option_default(self.target_cmd, tmp_path)

    def custom_teardown(self, tmp_path):
        self.my_locker.delete_item(self.good_template_name)
        super(TestEditBase, self).custom_teardown(tmp_path)

    def invoke(self, template: str = None):
        """
        Helper method for often repeated code in test methods
        :param template:
        :return:
        """
        args = [
            "--locker", self.locker_name,
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

    def common_pos_asserts(self, result, expected_content):
        assert result.exit_code == 0
        inst = self.my_locker.get_item(self.test_item_name)
        assert inst
        assert inst.content == expected_content


class TestEditNew(TestEditBase):

    def custom_setup(self, tmp_path):
        super(TestEditNew, self).custom_setup(tmp_path)

    def custom_teardown(self, tmp_path):
        super(TestEditNew, self).custom_teardown(tmp_path)

    def common_neg_asserts(self, result):
        super(TestEditNew, self).common_neg_asserts(result)
        with pytest.raises(PhibesNotFoundError):
            self.my_locker.get_item(self.test_item_name)

    def common_pos_asserts(self, result, expected_content):
        super(TestEditNew, self).common_pos_asserts(result, expected_content)

    @pytest.mark.negative
    def test_no_item(self, setup_and_teardown):
        """
        Simple case: Try to edit a non-existing item
        :param setup_and_teardown: injected fixture
        :return:
        """
        result = self.invoke()
        self.common_neg_asserts(result)


class TestEditExists(TestEditBase):

    def custom_setup(self, tmp_path):
        super(TestEditExists, self).custom_setup(tmp_path)
        my_item = self.my_locker.create_item(self.test_item_name)
        my_item.content = f"{self.test_item_name}"
        self.my_locker.add_item(my_item)

    def custom_teardown(self, tmp_path):
        super(TestEditExists, self).custom_teardown(tmp_path)

    def common_neg_asserts(self, result):
        super(TestEditExists, self).common_neg_asserts(result)

    def common_pos_asserts(self, result, expected_content):
        super(TestEditExists, self).common_pos_asserts(
            result, expected_content
        )

    def item_unchanged_asserts(self, before_item):
        after = self.my_locker.get_item(self.test_item_name)
        # the item still exists and hasn't changed
        assert after is not None
        assert before_item.content == after.content
        assert before_item.timestamp == after.timestamp

    @pytest.mark.positive
    def test_normal(self, tmp_path, datadir, setup_and_teardown):
        """
        Specify existing item
        :param tmp_path: pytest plugin injected
        :param datadir: pytest plugin injected
        :return:
        """
        before = self.my_locker.get_item(self.test_item_name)
        result = self.invoke()
        assert result.exit_code == 0, (
            f"{result.exception=}"
            f"{result.output=}"
        )
        inst = self.my_locker.get_item(self.test_item_name)
        assert inst
        assert 'happyclappy' in inst.content
        assert before.content in inst.content
