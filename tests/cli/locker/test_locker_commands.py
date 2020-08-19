"""
pytest module for phibes_cli locker commands
"""

# Standard library imports
# import shutil
import json

# Related third party imports
from click.testing import CliRunner

# Local application/library specific imports
from phibes.phibes_cli import main
from phibes.lib.config import Config
from phibes.lib.locker import Locker
from phibes.cli.locker.create import create_locker_cmd
from phibes.cli.locker.delete import delete_locker_cmd


def copy_config(source, target):
    my_conf = source.read()
    Config.write_config(target, **json.loads(my_conf))
    return


class TestCreateLocker(object):

    name = "new_locker"
    pw = "SmellyBeansVictor"

    def setup_method(self):
        try:
            Locker.delete(self.name, self.pw)
        except FileNotFoundError:
            pass
        return

    def teardown_method(self):
        try:
            Locker.delete(self.name, self.pw)
        except FileNotFoundError:
            pass
        return

    def test_create_locker(self, tmp_path, datadir, capsys):
        copy_config(datadir["phibes-config.json"], tmp_path)
        runner = CliRunner()
        result = runner.invoke(
            create_locker_cmd,
            [
                "--locker", self.name,
                "--password", self.pw
            ]
        )
        assert result.exit_code == 0
        assert "created" in result.output
        return


class TestDeleteLocker(object):

    name = "new_locker"
    pw = "SmellyBeansVictor"

    def setup_method(self):
        try:
            Locker.delete(self.name, self.pw)
        except FileNotFoundError:
            pass
        Locker(self.name, self.pw, create=True)
        return

    def teardown_method(self):
        try:
            Locker.delete(self.name, self.pw)
        except FileNotFoundError:
            pass
        return

    def test_delete_locker(self, tmp_path, datadir, capsys):
        copy_config(datadir["phibes-config.json"], tmp_path)
        runner = CliRunner()
        result = runner.invoke(
            delete_locker_cmd,
            ["--locker", self.name, "--password", self.pw]
        )
        assert result.exit_code == 0
        assert "deleted" in result.output
        return
