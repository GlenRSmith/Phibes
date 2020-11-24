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
from phibes.crypto.crypt_ifc import CryptIfc, HashIfc


class HashPlain(HashIfc):
    """
    Hashing class for retaining the original string in the "hash"
    """

    def __init__(self, **kwargs):
        super(HashPlain, self).__init__(**kwargs)
        self.length_bytes = kwargs.get('length_bytes')

    def hash_str(self, plaintext: str, **kwargs) -> str:
        """
        Hash the string
        @param plaintext: the string to hash
        @return: hashed string
        """
        salt = kwargs.get('salt')
        return f"{plaintext}-{salt}-{self.length_bytes}"


class CryptPlainPlain(CryptIfc):
    """
    Encryption implementation for no encryption
    """

    HashType = HashPlain
    salt_length_bytes = 4  # arbitrary choice

    def __init__(
            self,
            crypt_id: str,
            password: str,
            pw_hash: Optional[str] = None,
            salt: Optional[str] = None,
            **kwargs: dict
    ):
        super(CryptPlainPlain, self).__init__(
            crypt_id, password, pw_hash, salt, **kwargs
        )
        return

    @classmethod
    def create_salt(cls):
        """
        Convenience method to get salt of the right length.
        @return: new salt
        @rtype: str, with valid hexadecimal
        """
        return secrets.token_hex(cls.salt_length_bytes)

    def _hash_str(self, message, salt):
        return self._hasher.hash_str(message, salt=salt)

    def hash_name(self, name: str, salt: Optional[str] = None) -> str:
        """
        Hash an item that is a name
        @param name: The name
        @param salt: Optional salt
        @return: the hashed name
        """
        salt = (self.salt, salt)[bool(salt)]
        return self._hash_str(name, salt)

    def encrypt(self, plaintext: str, salt: Optional[str] = None) -> str:
        """
        Encrypt the plaintext
        @param plaintext: Text to encrypt
        @param salt: Optional salt
        @return: encrypted string
        """
        if salt:
            self.salt = salt
        val = plaintext.replace("\n", chr(31))
        return f"{val}{self.salt}"

    def decrypt(self, ciphertext: str, salt: Optional[str] = None) -> str:
        """
        Decrypt the ciphertext
        @param ciphertext: encrypted text
        @param salt: salt used in encryption
        @return: decrypted string
        """
        if salt:
            self.salt = salt
        val = ciphertext.replace(chr(31), "\n")
        return f"{val[:-len(self.salt)]}"

    def create_key(self, password: str, salt: str):
        return self._hash_str(password, salt)
