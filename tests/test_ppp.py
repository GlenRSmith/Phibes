"""
pytest module for ppp
"""

# Standard library imports
import json
import os
from pathlib import Path
import shutil
import tempfile

# Related third party imports
from click.testing import CliRunner
import pytest

# Local application/library specific imports
from privacy_playground.ppp import create_locker
from privacy_playground.lib.config import Config


DEFAULT_CONFIG = {
  "editor": "vim",
  "hash_locker_names": "False",
  "store_path": "."
}


def create_config_file():
    with open('pp-config.json', 'w') as f:
        f.write(json.dumps(DEFAULT_CONFIG))


@pytest.fixture
def change_working_dir():
    tmpdir = tempfile.mkdtemp(
        dir=Path.cwd().absolute()
    )
    os.chdir(tmpdir)
    return


# @contextlib.contextmanager
# def isolated_filesystem(self):
#     """A context manager that creates a temporary folder and changes
#     the current working directory to it for isolated filesystem tests.
#     """
#     cwd = os.getcwd()
#     t = tempfile.mkdtemp()
#     os.chdir(t)
#     try:
#         yield t
#     finally:
#         os.chdir(cwd)
#         try:
#             shutil.rmtree(t)
#         except (OSError, IOError):  # noqa: B014
#             pass


def test_create_locker(change_working_dir):
    runner = CliRunner()
    with runner.isolated_filesystem():
        create_config_file()
        result = runner.invoke(
            create_locker,
            [
                "--locker", "new_locker",
                "--password", "SmellyBeansVictor"
            ]
        )
        assert result.exit_code == 0
        assert "created" in result.output
    return



