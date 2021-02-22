"""
pytest module for phibes lib.config
"""

# Standard library imports
from pathlib import Path

# Related third party imports
import pytest

# Local application/library specific imports
from phibes.lib.config import ConfigModel
from phibes.lib.config import load_config_file


class TestConfig(object):

    @pytest.mark.positive
    def test_default_good(self, datadir):
        load_config_file(Path(datadir["default.json"]))
        test_config = ConfigModel()
        assert test_config.store_path == Path('.')

    @pytest.mark.positive
    def test_hash_false(self, datadir):
        load_config_file(Path(datadir["hash_false.json"]))
        test_config = ConfigModel()
        assert test_config.store_path == Path('.')

    @pytest.mark.positive
    def test_path_home(self, datadir):
        load_config_file(Path(datadir["path_home.json"]))
        test_config = ConfigModel()
        assert test_config.store_path == Path('~')
