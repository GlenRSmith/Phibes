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
from phibes.crypto.factory import CryptFactory
from phibes.crypto.crypt_aes_ctr_sha import AesCtrPbkdf2Sha
from phibes.lib.errors import PhibesAuthError
from phibes.model import Locker

# Local test imports
from tests.lib.test_helpers import EmptyLocker, plain_texts


class TestCryptImpl(object):

    def setup_method(self):
        self.pw = "s00p3rsekrit"
        self.crypts = {}
        for cid in list_crypts():
            crypt_impl = create_crypt(self.pw, crypt_id=cid)
            self.crypts[cid] = {
                'password': self.pw,
                'pw_hash': crypt_impl.pw_hash,
                'salt': crypt_impl.salt,
                'crypt_impl': crypt_impl
            }
        return

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plain_texts)
    def test_create_encrypt_decrypt(self, plaintext):
        for crypt_id in list_crypts():
            crypt = create_crypt(self.pw, crypt_id)
            step1 = crypt.encrypt(plaintext)
            step2 = crypt.decrypt(step1)
            assert step2 == plaintext, (
                f"{crypt=}\n"
                f"{plaintext=}\n"
                f"{step1=}\n"
                f"{step2=}\n"
            )

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plain_texts)
    def test_get_encrypt_decrypt(self, plaintext):
        for cid, rec in self.crypts.items():
            msg = f"{cid=} {rec=}"
            try:
                crypt = get_crypt(
                    cid, self.pw, rec['pw_hash'], rec['salt']
                )
                assert crypt.decrypt(crypt.encrypt(plaintext)) == plaintext, (
                    f"{msg}"
                )
            except PhibesAuthError as pae:
                pytest.fail(
                    f"{msg}\n{pae}\n{self.crypts}\n{list_crypts()}"
                    f"{CryptFactory()._objects[cid]}"
                )


    @pytest.mark.positive
    def test_multiple_cycles(self):
        """
        Ciphers can only be used once - CryptImpl is supposed to
        have a workaround that refreshes the cipher after each use
        :return:
        """
        crypt = create_crypt(self.pw)
        for tt in plain_texts:
            ct = crypt.encrypt(tt)
            pt = crypt.decrypt(ct)
            assert pt == tt
        for crypt_id in list_crypts():
            crypt = create_crypt(self.pw, crypt_id)
            crypt_id = crypt.crypt_id
            pw_hash = crypt.pw_hash
            salt = crypt.salt
            for tt in plain_texts:
                ct = crypt.encrypt(tt)
                pt = crypt.decrypt(ct)
                assert pt == tt
            crypt = get_crypt(crypt_id, self.pw, pw_hash, salt)
            for tt in plain_texts:
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
            Locker.get(password=wrong_pw, name=self.locker_name)
    @pytest.mark.positive
    def test_good_auth(self, setup_and_teardown):
        # auth is 'built in' to getting a crypt for existing locker
        assert Locker.get(name=self.locker_name, password=self.password)


class BadCrypt(AesCtrPbkdf2Sha):
    key_length_bytes = 32
    hash_alg = str(random.randint(1000, 9999))  # bad HashAlg on purpose


class TestCryptFallback(object):

    def setup_method(self):
        self.pw = "s00p3rsekrit"
        return

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plain_texts)
    def test_create_encrypt_decrypt(self, plaintext):
        try:
            crypt_id = register_crypt(
                BadCrypt,
                fallback_id=default_id,
                key_rounds=100100
            )
        except ValueError:
            crypt_id = "BadCryptkey_rounds100100"
        crypt = create_crypt(self.pw, crypt_id)
        assert crypt.decrypt(crypt.encrypt(plaintext)) == plaintext
