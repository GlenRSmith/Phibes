"""
pytest module for lib.crypto
"""

# Standard library imports

# Related third party imports
import pytest

# Local application/library specific imports
from privacy_playground.lib import crypto
# from privacy_playground.lib import locker
from locker_helper import EmptyLocker


class TestCryptImpl(object):

    def setup_method(self):
        self.pw = "This is just a test"
        self.impl = crypto.CryptImpl(
            self.pw,
            crypt_arg_is_key=False,
            salt='1c03cdbfc25c0b3007caa19d560b3d77'
        )
        self.salt = self.impl.salt
        self.key = self.impl.key

    def test_encrypt(self):
        plaintext = "This is just a test"
        ciphertext = self.impl.encrypt(plaintext)
        assert ciphertext == 'yYq48fG6KR65UTWfgGlGLQUBPQ=='

    def test_decrypt(self):
        ciphertext = 'yYq48fG6KR65UTWfgGlGLQUBPQ=='
        plaintext = self.impl.decrypt(ciphertext)
        assert plaintext == "This is just a test"

    def test_multiple_cycles(self):
        """
        Ciphers can only be used once - CryptImpl is supposed to
        have a workaround that refreshes the cipher after each use
        :return:
        """
        test_texts = [
            "This is just a test 1",
            "That is just a test 2",
            "We were just a test 3",
            "They will just be a test 4",
        ]
        for tt in test_texts:
            ct = self.impl.encrypt(tt)
            pt = self.impl.decrypt(ct)
            assert pt == tt


class TestCrypto(EmptyLocker):

    @pytest.mark.positive
    def test_make_salt_bytes(self):
        res = crypto.make_salt_bytes()
        assert type(res) is bytes

    @pytest.mark.positive
    def test_auth_password(self):
        # get the pw hash from making a locker
        # my_locker = locker.Locker('mylocker', self.password, create=True)
        salt = self.my_locker.salt
        # get the pw hash from making CryptImpl
        impl = crypto.CryptImpl(
            self.password, crypt_arg_is_key=False, salt=salt
        )
        # import pdb
        # pdb.set_trace()
        # impl.key  # this seems to be getting assigned bytes
        # impl.salt
        # impl.cipher
        # ciphertext = impl.
        # crypto.authenticate_password(pw, )
        return
