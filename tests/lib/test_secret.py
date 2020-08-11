"""
pytest module for lib.secret
"""

# Standard library imports

# Related third party imports

# Local application/library specific imports
from phibes.lib.secret import Secret
from locker_helper import EmptyLocker


class TestSecrets(EmptyLocker):

    def test_secrets(self):
        # create some secrets
        pth = self.my_locker.get_item_path("secret", "facebook")
        s1 = Secret(self.my_locker.crypt_key, "facebook")
        s1.content = "password:KidsBirthday"
        s1.save(pth)
        pth = self.my_locker.get_item_path("secret", "twitter")
        s2 = Secret(self.my_locker.crypt_key, "twitter")
        s2.content = "password:KidsBirthday"
        s2.save(pth)
        pth = self.my_locker.get_item_path("secret", "reddit")
        s3 = Secret(self.my_locker.crypt_key, "reddit")
        s3.content = "password:KidsBirthday"
        s3.save(pth)
        # TestSecrets.my_locker.add_item(s1)
        # TestSecrets.my_locker.add_item(s2)
        # TestSecrets.my_locker.add_item(s3)
