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
    """
    Hashing class for retaining the original string in the "hash"
    """

    def __init__(self, **kwargs):
        super(HashPlain, self).__init__(**kwargs)
        self.length_bytes = kwargs.get('length_bytes')

    def hash_str(
            self, plaintext: str, salt: str
    ) -> str:
        """
        Hash the string
        @param plaintext: the string to hash
        @param salt: salt value
        @return: hashed string
        """
        return f"{plaintext}-{salt}-{self.length_bytes}"


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
        val = plaintext.replace("\n", chr(31))
        return f"{val}{salt}"

    def decrypt(self, ciphertext: str, salt: Optional[str] = None) -> str:
        val = ciphertext.replace(chr(31), "\n")
        return f"{val.rstrip(salt)}"


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
        self._hasher = HashPlain(**kwargs)
        self._crypter = CryptPlain('', salt)
        # self.key = key
        self.pw_hash = "pw_hash"
        self.salt = ("salt", salt)[salt is not None]
        return

    def _hash_str(self, message, salt, length):
        return self._hasher.hash_str(message, salt)

    def hash_name(self, name: str, salt: Optional[str] = '0000') -> str:
        """
        Hash an item that is a name
        @param name: The name
        @param salt: Optional salt
        @return: the hashed name
        """
        return self._hash_str(name, salt, 8)

    def encrypt(self, plaintext: str, salt: Optional[str] = None) -> str:
        """
        Encrypt the plaintext using self._crypter
        @param plaintext: Text to encrypt
        @param salt: Optional salt
        @return: encrypted string
        """
        salt = ('', salt)[bool(salt)]
        return self._crypter.encrypt(plaintext, salt)

    def decrypt(self, ciphertext: str, salt: Optional[str] = None) -> str:
        """
        Decrypt the ciphertext using self._crypter
        @param ciphertext: encrypted text
        @param salt: salt used in encryption
        @return: decrypted string
        """
        salt = ('', salt)[bool(salt)]
        return self._crypter.decrypt(ciphertext, salt)
