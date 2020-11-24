"""
pytest module for assuring
pytest -m 'not positive and not negative'
doesn't exit 5 (no tests collected)
"""

# Standard library imports

# Related third party imports
import pytest

# Local application/library specific imports


class TestNothing:

    @pytest.mark.nothing
    def test_nothing(self):
        pass
