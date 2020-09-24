"""
pytest module for lib.crypto
"""

# Standard library imports
import random

# Related third party imports
import pytest

# Local application/library specific imports
from phibes.crypto import create_crypt, default_id, get_crypt, list_crypts
from phibes.crypto import register_crypt
from phibes.crypto.crypt_aes_ctr_sha256 import CryptAesCtrPbkdf2Sha
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
        self.crypts = {}
        for cid in list_crypts():
            crypt_impl = create_crypt(self.pw, crypt_id=cid)
            self.crypts[cid] = {
                'pw_hash': crypt_impl.pw_hash,
                'salt': crypt_impl.salt
            }
        return

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plains)
    def test_create_encrypt_decrypt(self, plaintext):
        for crypt_id in list_crypts():
            crypt = create_crypt(self.pw, crypt_id)
            assert crypt.decrypt(crypt.encrypt(plaintext)) == plaintext

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plains)
    def test_get_encrypt_decrypt(self, plaintext):
        for cid, rec in self.crypts.items():
            crypt = get_crypt(
                cid, self.pw, rec['pw_hash'], rec['salt']
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
        for crypt_id in list_crypts():
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
            Locker.get(self.locker_name, wrong_pw)

    @pytest.mark.positive
    def test_good_auth(self, setup_and_teardown):
        # auth is 'built in' to getting a crypt for existing locker
        assert Locker.get(self.locker_name, self.password)


class TestCryptFallback(object):

    def setup_method(self):
        self.pw = "s00p3rsekrit"
        return

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plains)
    def test_create_encrypt_decrypt(self, plaintext):
        crypt_id = register_crypt(
            CryptAesCtrPbkdf2Sha,
            fallback_id=default_id,
            key_rounds=100100,
            hash_alg=str(random.randint(1000, 9999))
        )
        crypt = create_crypt(self.pw, crypt_id)
        assert crypt.decrypt(crypt.encrypt(plaintext)) == plaintext
