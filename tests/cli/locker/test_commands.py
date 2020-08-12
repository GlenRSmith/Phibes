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
from phibes.lib.locker import Locker
from phibes.cli.locker.commands import create_locker


def copy_config(source, target):
    my_conf = source.read()
    Config.write_config(target, **json.loads(my_conf))
    return


class TestCreateLocker(object):

    name = "new_locker"
    pw = "SmellyBeansVictor"

    @staticmethod
    def setup_method():
        try:
            Locker.delete(TestCreateLocker.name, TestCreateLocker.pw)
        except FileNotFoundError:
            pass
        return

    @staticmethod
    def teardown_method():
        Locker.delete(TestCreateLocker.name, TestCreateLocker.pw)
        return

    def test_create_locker(self, tmp_path, datadir, capsys):
        copy_config(datadir["phibes-config.json"], tmp_path)
        with capsys.disabled():
            runner = CliRunner()
            result = runner.invoke(
                create_locker,
                [
                    "--locker", TestCreateLocker.name,
                    "--password", TestCreateLocker.pw
                ]
            )
            assert result.exit_code == 0
            assert "created" in result.output
        return
