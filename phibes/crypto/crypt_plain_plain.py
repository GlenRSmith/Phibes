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
from phibes.lib.errors import PhibesAuthError


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

    salt_length_bytes = 16  # arbitrary choice

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

    @property
    def salt(self):
        return self._salt

    @salt.setter
    def salt(self, new_salt: str):
        salt = (new_salt, self.create_salt())[new_salt is None]
        if len(bytes.fromhex(salt)) != self.salt_length_bytes:
            raise ValueError(
                f"salt {new_salt} is {len(bytes.fromhex(salt))} bytes long\n"
                f"{self.salt_length_bytes} bytes required\n"
            )
        self._salt = salt

    def __init__(self, key: str, salt: Optional[str] = None, **kwargs):
        super(CryptPlain, self).__init__(key, salt, **kwargs)
        self.key = key
        self.salt = salt
        return

    @classmethod
    def create_salt(cls):
        """
        Convenience method to get salt of the right length.
        @return: new salt
        @rtype: str, with valid hexadecimal
        """
        return secrets.token_hex(cls.salt_length_bytes)

    def encrypt(self, plaintext: str, salt: Optional[str] = None) -> str:
        if salt:
            self.salt = salt
        val = plaintext.replace("\n", chr(31))
        return f"{val}{self.salt}"

    def decrypt(self, ciphertext: str, salt: Optional[str] = None) -> str:
        if salt:
            self.salt = salt
        val = ciphertext.replace(chr(31), "\n")
        return f"{val[:-len(self.salt)]}"


class CryptPlainPlain(CryptIfc):
    """
    Encryption implementation for no encryption
    """

    @property
    def salt(self):
        """
        salt property accessor
        :return:
        """
        return self._crypter.salt

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
        creating = password and not pw_hash and not salt
        if not (password and pw_hash and salt) and not creating:
            pref = f"{self.__class__.__name__}\n"
            raise ValueError(
                f"invalid call to __init__\n"
                f"valid calls are are:\n"
                f"{pref}(password)\n"
                f"{pref}(password, pw_hash, salt)\n"
                f"{password=} {pw_hash=} {salt=} {kwargs=}"
            )
        self._hasher = HashPlain(**kwargs)
        if creating:
            salt = CryptPlain.create_salt()
        key = self._hasher.hash_str(password, salt)
        self._crypter = CryptPlain(key, salt)
        auth_key = self.encrypt(self.hash_name(password, salt))
        if not creating:
            if not auth_key == pw_hash:
                raise PhibesAuthError(
                    f"{pw_hash} does not match {auth_key}"
                )
        self.pw_hash = auth_key
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
        return self._crypter.encrypt(plaintext, salt)

    def decrypt(self, ciphertext: str, salt: Optional[str] = None) -> str:
        """
        Decrypt the ciphertext using self._crypter
        @param ciphertext: encrypted text
        @param salt: salt used in encryption
        @return: decrypted string
        """
        return self._crypter.decrypt(ciphertext, salt)
