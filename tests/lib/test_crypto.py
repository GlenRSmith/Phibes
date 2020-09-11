"""
pytest module for lib.crypto
"""

# Standard library imports

# Related third party imports
import pytest

# Local application/library specific imports
from phibes.crypto import CryptFactory
from phibes.crypto import create_crypt, get_crypt
from phibes.lib.errors import PhibesAuthError
from phibes.model import Locker

# Local test imports
from tests.lib.locker_helper import EmptyLocker


plains = [
    "Easy Peasy",
    "this is my password for bouncycastledelivery.com",
    "this is my password \t for bouncycastledelivery.com",
    "this is my password \n for bouncycastledelivery.com",
    "This is just a test 1",
    "That is just a test 2",
    "We were just a test 3",
    "They will just be a test 4",
    """
    site:www.bouncycastledelivery.com
    username:Jenny'sMomAndDad
    password:WeWantToThrowtheb3stbirthdayparty07
    """,
    """
    {
        'site':'www.bouncycastledelivery.com',
        'username':'Jenny'sMomAndDad',
        'password':'WeWantToThrowtheb3stbirthdayparty07'
    }
    """
]


class TestCryptImpl(object):

    def setup_method(self):
        self.pw = "s00p3rsekrit"
        crypt_impl = create_crypt(self.pw)
        self.crypt_id = crypt_impl.crypt_id
        self.pw_hash = crypt_impl.pw_hash
        self.salt = crypt_impl.salt
        return

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plains)
    def test_create_encrypt_decrypt(self, plaintext):
        for crypt_id in CryptFactory().list_builders():
            crypt = create_crypt(self.pw, crypt_id)
            assert crypt.decrypt(crypt.encrypt(plaintext)) == plaintext

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plains)
    def test_get_encrypt_decrypt(self, plaintext):
        for crypt_id in CryptFactory().list_builders():
            crypt = get_crypt(
                crypt_id, self.pw, self.pw_hash, self.salt
            )
            assert crypt.decrypt(crypt.encrypt(plaintext)) == plaintext

    @pytest.mark.positive
    def test_multiple_cycles(self):
        """
        Ciphers can only be used once - CryptImpl is supposed to
        have a workaround that refreshes the cipher after each use
        :return:
        """
        crypt = create_crypt(self.pw)
        for tt in plains:
            ct = crypt.encrypt(tt)
            pt = crypt.decrypt(ct)
            assert pt == tt
        for crypt_id in CryptFactory().list_builders():
            crypt = create_crypt(self.pw, crypt_id)
            crypt_id = crypt.crypt_id
            pw_hash = crypt.pw_hash
            salt = crypt.salt
            for tt in plains:
                ct = crypt.encrypt(tt)
                pt = crypt.decrypt(ct)
                assert pt == tt
            crypt = get_crypt(crypt_id, self.pw, pw_hash, salt)
            for tt in plains:
                ct = crypt.encrypt(tt)
                pt = crypt.decrypt(ct)
                assert pt == tt


class TestCrypto(EmptyLocker):

    @pytest.mark.positive
    def test_what(self):
        pw = "this right here"
        crypt = create_crypt(pw)
        file_pw_hash = crypt.pw_hash
        crypt_id = crypt.crypt_id
        file_salt = crypt.salt
        crypt = get_crypt(
            crypt_id, pw, file_pw_hash, file_salt
        )
        assert crypt

    @pytest.mark.negative
    def test_fail_auth(self, tmp_path, setup_and_teardown):
        wrong_pw = "ThisWillNotBeIt"
        with pytest.raises(PhibesAuthError):
            Locker(
                self.locker_name, wrong_pw, create=False
            )

    @pytest.mark.positive
    def test_good_auth(self, setup_and_teardown):
        # auth is 'built in' to getting a crypt for existing locker
        assert Locker(self.locker_name, self.password, create=False)
