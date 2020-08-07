"""
pytest module for lib.phibes_file
"""

# Standard library imports
from pathlib import Path

# Related third party imports
import pytest

# Local application/library specific imports
from privacy_playground.lib import phibes_file


class TestPhibesFile(object):

    test_salt = "1233485123"
    test_timestamp = "timestamp"
    test_body = "Lorem ipsum dolor sit amet, ex eum tollit laoreet"
    test_file = "test_phibes_test.tmp"
    pth = Path('.').joinpath(test_file)

    def setup_method(self):
        if self.pth.exists():
            self.pth.unlink()

    def teardown_method(self):
        if self.pth.exists():
            self.pth.unlink()

    def test_write_new_read(self):
        phibes_file.write(
            self.pth,
            salt=self.test_salt,
            timestamp=self.test_timestamp,
            body=self.test_body
        )
        result = phibes_file.read(self.pth)
        assert result['body'] == self.test_body
        assert result['salt'] == self.test_salt
        assert result['timestamp'] == self.test_timestamp

    def test_write_no_body(self):
        with pytest.raises(AttributeError):
            phibes_file.write(
                self.pth,
                salt=self.test_salt,
                timestamp=self.test_timestamp,
                body=""
            )

    def test_forbid_newlines(self):
        with pytest.raises(ValueError):
            phibes_file.write(
                self.pth,
                salt=self.test_salt,
                timestamp=self.test_timestamp,
                body=(
                    f"{self.test_body}\n"
                    f"{self.test_body}"
                )
            )

    def test_forbid_overwrite(self):
        phibes_file.write(
            self.pth,
            salt=self.test_salt,
            timestamp=self.test_timestamp,
            body=f"{self.test_body}"
        )
        with pytest.raises(FileExistsError):
            phibes_file.write(
                self.pth,
                salt=self.test_salt,
                timestamp=self.test_timestamp,
                body=f"{self.test_body}"
            )

    def test_allow_overwrite(self):
        phibes_file.write(
            self.pth,
            salt=self.test_salt,
            timestamp=self.test_timestamp,
            body=f"{self.test_body}"
        )
        phibes_file.write(
            self.pth,
            salt=self.test_salt,
            timestamp=self.test_timestamp,
            body="replacement",
            overwrite=True
        )
        result = phibes_file.read(self.pth)
        assert result['salt'] == self.test_salt
        assert result['timestamp'] == self.test_timestamp
        assert result['body'] == 'replacement'

