"""
pytest module for ppp
"""

# Standard library imports
from pathlib import Path
import os

# Related third party imports
import pytest

# Local application/library specific imports
from ..import ppp
from ..lib.config import Config


def test_nothing():
    return


def test_create_locker():
    return


class TestConfig:

    def test_default_good(self):
        """
        Test depends on default pp-config.json in project root, and for
        Config class to set properties in specific ways
        :return:
        """
        test_config = Config()
        assert test_config.editor == 'vim'
        assert test_config.hash_locker_names
        assert test_config.store_path == Path('.')

    def test_override_file(self):
        """
        Test depends on pp-config.json in test dir, and for
        Config class to set properties in specific ways
        :return:
        """
        my_file = Path('.').joinpath('tests').joinpath('pp-config-other.json')
        test_config = Config(my_file)
        assert test_config.editor == 'other'
        assert not test_config.hash_locker_names
        assert test_config.store_path == Path('.')

    def test_override_directory(self):
        """
        Test depends on pp-config.json in test dir, and for
        Config class to set properties in specific ways
        :return:
        """
        os.chdir('tests')
        test_config = Config()
        assert test_config.editor == 'vim'
        assert not test_config.hash_locker_names
        assert test_config.store_path == Path('.')

