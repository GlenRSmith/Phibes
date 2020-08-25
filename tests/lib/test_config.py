"""
pytest module for phibes lib.config
"""

# Standard library imports
from pathlib import Path

# Related third party imports

# Local application/library specific imports
from phibes.lib.config import ConfigModel
from phibes.lib.config import load_config_file


class TestConfig(object):

    def test_default_good(self, datadir):
        load_config_file(Path(datadir["default.json"]))
        test_config = ConfigModel()
        assert test_config.editor == 'vim'
        assert test_config.hash_locker_names
        assert test_config.store_path == Path('.')

    def test_hash_false(self, datadir):
        load_config_file(Path(datadir["hash_false.json"]))
        test_config = ConfigModel()
        assert test_config.editor == 'vim'
        assert not test_config.hash_locker_names
        assert test_config.store_path == Path('.')

    def test_path_home(self, datadir):
        load_config_file(Path(datadir["path_home.json"]))
        test_config = ConfigModel()
        assert test_config.editor == 'vim'
        assert test_config.hash_locker_names
        assert test_config.store_path == Path('~')
