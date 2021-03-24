"""
pytest module for phibes_cli create-item command
"""

# Standard library imports
from typing import Callable

# Related third party imports
import click
from click.testing import CliRunner
import pytest

# Local application/library specific imports
from phibes import phibes_cli
from phibes.cli.cli_config import CliConfig
from phibes.cli.commands import Action, Target
from phibes.cli.commands import build_cli_app
from phibes.cli import handlers
from phibes.cli.lib import main as main_anon
from phibes.cli.lib import PhibesCliError
from phibes.crypto import list_crypts
from phibes.lib.errors import PhibesNotFoundError
from phibes.lib.config import write_config_file
from phibes.model import Locker, LOCKER_FILE

# Local test imports
from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.test_helpers import BaseAnonLockerTest
from tests.lib.test_helpers import PopulatedLocker


def make_single_command_cli_app(
        group: click.group,
        target: Target,
        action: Action,
        sub_cmd: str,
        func: Callable,
        named_locker: bool
):
    return build_cli_app(
        command_dict={target: {action: {'name': sub_cmd, 'func': func}}},
        click_group=group,
        named_locker=named_locker
    )


class TestNoName(BaseAnonLockerTest):

    password = "78CollECtion!CampCoolio"
    command_name = 'test_create_item'
    target = Target.Item
    action = Action.Create
    func = handlers.create_item
    click_group = main_anon
    test_item_name = 'gonna_addit'

    def custom_setup(self, tmp_path):
        super(TestNoName, self).custom_setup(tmp_path)
        conf = CliConfig()
        conf.store = {
            'store_type': conf.store['store_type'],
            'store_path': tmp_path
        }
        # conf.store_path = tmp_path
        conf.editor = 'echo happyclappy>> '
        write_config_file(tmp_path, update=True)

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
        if 'template' in arg_dict:
            args += ["--template", arg_dict['template']]
        return CliRunner().invoke(
            self.click_group.commands[self.command_name], args
        )

    def prep_and_run(self, arg_dict):
        self.my_locker = Locker.create(
            password=self.password, crypt_id=arg_dict['crypt_id']
        )
        # change the configured working path to the test directory
        update_config_option_default(
            self.click_group.commands[self.command_name],
            self.test_path
        )
        return self.invoke(arg_dict=arg_dict)

    @pytest.mark.parametrize("crypt_id", list_crypts())
    @pytest.mark.positive
    def test_found(self, crypt_id, setup_and_teardown):
        result = self.prep_and_run({'crypt_id': crypt_id})
        assert result
        assert result.exit_code == 0, (
            f"{crypt_id=}\n"
            f"{result.exception=}\n"
            f"{result.output=}\n"
        )
        locker_inst = Locker.get(password=self.password, locker_name=None)
        assert (
                locker_inst.data_model.storage.locker_file ==
                self.test_path / LOCKER_FILE
        )
        item_inst = self.my_locker.get_item(self.test_item_name)
        assert item_inst
        assert item_inst.content == 'happyclappy\n'


class TestCreateBase(PopulatedLocker):

    test_item_name = 'gonna_edit'
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
        CliConfig().editor = 'echo happyclappy>> '
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
        assert result.exit_code == 1, result.output
        assert result.exception, result.output
        assert isinstance(result.exception, PhibesCliError)
        return

    def common_pos_asserts(self, result, expected_content, locker_inst=None):
        assert result.exit_code == 0, (
            f"{result.exception=}\n"
            f"{result.output=}\n"
        )
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
