"""
pytest module for lib.secret
"""

# Standard library imports

# Related third party imports

# Local application/library specific imports
from privacy_playground.lib.secret import Secret
from locker_helper import LockerHelper


class TestSecrets(LockerHelper):

    def test_secrets(self):
        # create some secrets
        s1 = Secret(TestSecrets.my_locker, "facebook", create=True)
        s2 = Secret(TestSecrets.my_locker, "twitter", create=True)
        s3 = Secret(TestSecrets.my_locker, "reddit", create=True)
