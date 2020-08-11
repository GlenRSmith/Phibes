"""
pytest module for ppp
"""

# Standard library imports
# import shutil
import json

# Related third party imports
from click.testing import CliRunner

# Local application/library specific imports
from phibes.lib.config import Config
from phibes.lib.locker import Locker
from phibes.ppp import create_locker


def copy_config(source, target):
    my_conf = source.read()
    Config.write_config(target, **json.loads(my_conf))
    return


# datadirs = [
#     ('tests.test_ppp/TestCreateLocker/test_create_locker'),
#     ('tests.test_ppp/TestCreateLocker'),
#     ('tests.test_ppp'),
#     ('data/tests.test_ppp/TestCreateLocker/test_create_locker'),
#     ('data/tests.test_ppp/TestCreateLocker'),
#     ('data/tests.test_ppp'),
#     ('data')
# ]


class TestCreateLocker(object):

    name = "new_locker"
    pw = "SmellyBeansVictor"

    def setup_method(self):
        try:
            Locker.delete(TestCreateLocker.name, TestCreateLocker.pw)
        except FileNotFoundError:
            pass
        return

    def teardown_method(self):
        Locker.delete(
            TestCreateLocker.name, TestCreateLocker.pw
        )
        return

    def test_create_locker(self, tmp_path, datadir, capsys):
        copy_config(datadir["pp-config.json"], tmp_path)
        with capsys.disabled():
            test_config = Config(tmp_path)
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


class TestEdit(object):

    def test_edit(self):
        return
