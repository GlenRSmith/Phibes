"""
Encryption classes for AES encryption
"""

# Built-in library packages
from __future__ import annotations
import abc
import base64
import secrets
from typing import Optional

# Third party packages
from Cryptodome.Cipher import AES
from Cryptodome.Util import Counter

# In-project modules


# If this stays, it belongs in a more general file
class EncryptionIfc(abc.ABC):

    @abc.abstractmethod
    def __init__(self, key: str, salt: Optional[str] = None, **kwargs):
        pass

    @abc.abstractmethod
    def encrypt(self, plaintext: str, salt: str) -> str:
        pass

    @abc.abstractmethod
    def decrypt(self, ciphertext: str, salt: str) -> str:
        pass


class CryptAesCtrmode(EncryptionIfc, abc.ABC):
    """
    Encryption implementation for AES256 encryption with mode=Counter
    """
    # AES.block_size = 16
    salt_length_bytes = AES.block_size
    key_length_bytes = AES.block_size * 2

    @property
    def cipher(self):
        """
        cipher property accessor
        :return:
        """
        return AES.new(
            key=bytes.fromhex(self.key),
            mode=AES.MODE_CTR,
            counter=Counter.new(
                AES.block_size * 8,
                initial_value=int.from_bytes(
                    bytes.fromhex(self.salt), "big"
                )
            )
        )

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
        if len(new_key) != CryptAesCtrmode.key_length_bytes * 2:
            raise ValueError(
                f"`key` {new_key} is {len(new_key) / 2} bytes long\n"
                f"{AES.block_size} bytes required\n"
            )
        self._key = new_key

    @property
    def salt(self):
        """
        salt property accessor
        :return:
        """
        return self._salt

    @salt.setter
    def salt(self, new_salt: Optional[str]):
        """
        salt property mutator
        assign `None` to get it to regenerate itself!
        :param new_salt:
        :return:
        """
        salt = (new_salt, self.create_salt())[new_salt is None]
        if len(salt) != CryptAesCtrmode.salt_length_bytes * 2:
            raise ValueError(
                f"`salt` {new_salt} is {len(new_salt) / 2} bytes long\n"
                f"{CryptAesCtrmode.salt_length_bytes} bytes required\n"
            )
        self._salt = salt
        return

    def __init__(self, key: str, salt: Optional[str] = None, **kwargs):
        super(CryptAesCtrmode, self).__init__(key, salt, **kwargs)
        self.key = key
        # assigning None triggers creating new value; see salt.setter
        self.salt = salt
        return

    @staticmethod
    def create_salt():
        """
        Convenience method to get salt of the right length.
        @return: new salt
        @rtype: str, with valid hexadecimal
        """
        return secrets.token_hex(CryptAesCtrmode.salt_length_bytes)

    def encrypt(self, plaintext: str, salt: Optional[str] = None) -> str:
        if salt:
            self.salt = salt
        # convert from str to bytes
        plaintext_bytes = plaintext.encode('utf-8')
        # run the actual encryption - it gets bytes, returns bytes
        cipherbytes = self.cipher.encrypt(plaintext_bytes)
        # substitute for chars that aren't file-system safe
        # e.g. - instead of + and _ instead of /
        # bytes in, bytes returned
        fs_safe_cipherbytes = base64.urlsafe_b64encode(cipherbytes)
        # convert the bytes to a utf-8 str
        return fs_safe_cipherbytes.decode('utf-8')

    def decrypt(self, ciphertext: str, salt: Optional[str] = None) -> str:
        if salt:
            self.salt = salt
        # reverse the steps in `encrypt`
        # convert from str to bytes
        fs_safe_cipherbytes = ciphertext.encode('utf-8')
        # char substitution back to + and /
        cipherbytes = base64.urlsafe_b64decode(fs_safe_cipherbytes)
        # run the actual decryption
        plaintext_bytes = self.cipher.decrypt(cipherbytes)
        # convert the bytes to utf-8 str
        return plaintext_bytes.decode('utf-8')
