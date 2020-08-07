"""
pytest module for ppp lib.config
"""

# Standard library imports
import json
from pathlib import Path

# Related third party imports

# Local application/library specific imports
from privacy_playground.lib.config import Config


def copy_config(source, target):
    my_conf = source.read()
    Config.write_config(target, **json.loads(my_conf))
    return


class TestConfig(object):

    def test_default_good(self, tmp_path, datadir):
        copy_config(datadir["default.json"], tmp_path)
        test_config = Config(tmp_path)
        assert test_config.editor == 'vim'
        assert test_config.hash_locker_names
        assert test_config.store_path == Path('.')

    def test_hash_false(self, tmp_path, datadir):
        copy_config(datadir["hash_false.json"], tmp_path)
        test_config = Config(tmp_path)
        assert test_config.editor == 'vim'
        assert not test_config.hash_locker_names
        assert test_config.store_path == Path('.')

    def test_path_home(self, tmp_path, datadir):
        copy_config(datadir["path_home.json"], tmp_path)
        test_config = Config(tmp_path)
        assert test_config.editor == 'vim'
        assert test_config.hash_locker_names
        assert test_config.store_path == Path('~')
