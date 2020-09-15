"""
pytest module for lib.secret
"""

# Standard library imports

# Related third party imports
import pytest

# Local application/library specific imports
from phibes.model import Secret

# Local test imports
from tests.lib.locker_helper import EmptyLocker


class TestSecrets(EmptyLocker):

    @pytest.mark.positive
    def test_secrets(self, setup_and_teardown):
        # create some secrets
        pth = self.my_locker.get_item_path("secret", "facebook")
        s1 = Secret(self.my_locker.crypt_impl, "facebook")
        s1.content = "password:KidsBirthday"
        s1.save(pth)
        pth = self.my_locker.get_item_path("secret", "twitter")
        s2 = Secret(self.my_locker.crypt_impl, "twitter")
        s2.content = "password:KidsBirthday"
        s2.save(pth)
        pth = self.my_locker.get_item_path("secret", "reddit")
        s3 = Secret(self.my_locker.crypt_impl, "reddit")
        s3.content = "password:KidsBirthday"
        s3.save(pth)
        # TestSecrets.my_locker.add_item(s1)
        # TestSecrets.my_locker.add_item(s2)
        # TestSecrets.my_locker.add_item(s3)
