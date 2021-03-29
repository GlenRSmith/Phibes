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
from phibes.crypto.crypt_ifc import CryptIfc


def hash_str(plaintext: str, salt: str, length_bytes: int) -> str:
    """
    Hash the string
    :param plaintext: string to hash
    :param salt:
    :param length_bytes:
    :return:
    """
    return f"{plaintext}-{salt}-{length_bytes}"


class CryptPlainPlain(CryptIfc):
    """
    Encryption implementation for no encryption
    """

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

    def hash_name(self, name: str, salt: str) -> str:
        """
        Hash an item that is a name
        @param name: The name
        @param salt: salt
        @return: the hashed name
        """
        return hash_str(name, salt, self.salt_length_bytes)

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
        return hash_str(password, salt, self.salt_length_bytes)
