"""
pytest module for phibes_cli locker delete command
"""

# Standard library imports

# Related third party imports
from click.testing import CliRunner
import pytest

# Local application/library specific imports
from phibes.phibes_cli import main
from phibes.lib.locker import Locker
from phibes.cli.locker.delete import delete_locker_cmd
from tests.lib.locker_helper import BaseTestClass
from tests.lib.locker_helper import setup_and_teardown


used = setup_and_teardown


class TestDeleteLocker(BaseTestClass):

    name = "new_locker"
    pw = "SmellyBeansVictor"
    test_config = {
        "editor": "vim",
        "hash_locker_names": "False",
        "store_path": "."
    }

    def custom_setup(self, tmp_path):
        super(TestDeleteLocker, self).custom_setup(tmp_path)
        try:
            Locker.delete(self.name, self.pw)
        except FileNotFoundError:
            pass
        Locker(self.name, self.pw, create=True)
        return

    def custom_teardown(self):
        try:
            Locker.delete(self.name, self.pw)
        except FileNotFoundError:
            pass
        return

    @pytest.mark.parametrize(
        "command_instance", [delete_locker_cmd, main.commands['delete-locker']]
    )
    def test_delete_locker_main(
            self, setup_and_teardown, tmp_path, command_instance
    ):
        inst = Locker(self.name, self.pw)
        assert inst
        result = CliRunner().invoke(
            command_instance,
            [
                "--config", tmp_path,
                "--locker", self.name,
                "--password", self.pw
            ]
        )
        assert result.exit_code == 0
        with pytest.raises(FileNotFoundError):
            Locker(self.name, self.pw)
        return
