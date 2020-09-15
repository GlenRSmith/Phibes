"""
Encryption classes for plain text.
Basically no-op for everything
"""

# Built-in library packages
from __future__ import annotations
import secrets
from typing import Optional

# Third party packages

# In-project modules
from phibes.crypto.crypt_ifc import CryptIfc, EncryptionIfc, HashIfc


class HashPlain(HashIfc):

    def __init__(self, **kwargs):
        super(HashPlain, self).__init__(**kwargs)

    def hash_str(
            self, plaintext: str, salt: str, rounds: int, length_bytes: int
    ) -> str:
        return f"{plaintext}, {salt}, {rounds}, {length_bytes}"


class CryptPlain(EncryptionIfc):
    """
    Encryption implementation for no encryption
    """

    @property
    def key(self):
        """
        key property accessor
        :return:
        """
        return self._key

    @key.setter
    def key(self, new_key):
        """
        key property mutator
        :param new_key:
        :return:
        """
        self._key = new_key

    def __init__(self, key: str, salt: Optional[str] = None, **kwargs):
        super(CryptPlain, self).__init__(
            key, salt, **kwargs)
        self.key = key
        self.salt = salt
        return

    @staticmethod
    def create_salt():
        """
        Convenience method to get salt of the right length.
        @return: new salt
        @rtype: str, with valid hexadecimal
        """
        return secrets.token_hex(16)

    def encrypt(self, plaintext: str, salt: Optional[str] = None) -> str:
        return f"{plaintext}{salt}"

    def decrypt(self, ciphertext: str, salt: Optional[str] = None) -> str:
        return ciphertext[0:-len(salt)]


class CryptPlainPlain(CryptIfc):
    """
    Encryption implementation for no encryption
    """

    def __init__(
            self,
            password: str,
            pw_hash: Optional[str] = None,
            salt: Optional[str] = None,
            **kwargs: dict
    ):
        super(CryptPlainPlain, self).__init__(
            password, pw_hash, salt, **kwargs
        )
        self._hasher = HashPlain()
        self._crypter = CryptPlain('', salt)
        # self.key = key
        self.pw_hash = pw_hash
        self.salt = salt
        return

    def _hash_str(self, message, salt, length):
        return self._hasher.hash_str(message, salt, length)

    def hash_name(self, name: str, salt: Optional[str] = '0000') -> str:
        return self._hash_str(name, salt, 8)

    def encrypt(self, plaintext: str, salt: Optional[str] = None) -> str:
        salt = ('', salt)[bool(salt)]
        return f"{plaintext}{salt}"

    def decrypt(self, ciphertext: str, salt: Optional[str] = None) -> str:
        salt = ('', salt)[bool(salt)]
        return ciphertext.rstrip(salt)


def decrypt(ciphertext: str, salt: str) -> str:
    return ciphertext[0:-len(salt)]


def plain_encrypt(plaintext: str, salt: str) -> str:
    return f"{plaintext}{salt}"
