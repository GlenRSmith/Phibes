"""
pytest module for lib.crypt_impl
"""

# Standard library imports
import json

# Related third party imports

# Local application/library specific imports
# from privacy_playground.lib.locker import Locker
from privacy_playground.lib import crypt_impl


class TestCryptImple(object):

    def setup_method(self):
        self.pw = "This is just a test"
        self.salt = "1234abcddeadbeef"
        self.key = crypt_impl.make_crypt_key(self.pw, self.salt)
        self.impl = crypt_impl.CryptImpl(
            self.key, crypt_arg_is_key=True, iv=self.salt
        )

    def test_encrypt(self):
        plaintext = "This is just a test"
        ciphertext = self.impl.encrypt(plaintext)
        assert ciphertext == '4utME4nulSvCt-65OmM7daAR9w=='

    def test_decrypt(self):
        ciphertext = '4utME4nulSvCt-65OmM7daAR9w=='
        plaintext = self.impl.decrypt(ciphertext)
        assert plaintext == "This is just a test"
