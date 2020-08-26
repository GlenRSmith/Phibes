"""
pytest module for lib.crypto
"""

# Standard library imports

# Related third party imports
import pytest

# Local application/library specific imports
from phibes.lib import crypto
from phibes.lib import locker

# Local test imports
from tests.lib.locker_helper import EmptyLocker


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

    @pytest.mark.positive
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
    def test_what(self):
        pw = "this right here"
        impl = crypto.CryptImpl(pw, crypt_arg_is_key=False)
        cipher = impl.encrypt_password(pw)
        assert impl.authenticate(pw, cipher)

    @pytest.mark.positive
    def test_make_salt_bytes(self):
        res = crypto.make_salt_bytes()
        assert type(res) is bytes

    @pytest.mark.negative
    def test_fail_auth(self, tmp_path, setup_and_teardown):
        wrong_pw = "ThisWillNotBeIt"
        with pytest.raises(ValueError):
            locker.Locker(
                self.locker_name, wrong_pw, create=False
            )

    @pytest.mark.positive
    def test_good_auth(self, setup_and_teardown):
        assert locker.Locker(
            self.locker_name, self.password, create=False
        )
