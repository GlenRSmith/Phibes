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
from phibes.crypto.crypt_ifc import EncryptionIfc


class AesCtrIfc(EncryptionIfc):
    """
    Encryption implementation for AES encryption with mode=Counter
    """

    iv_length_bytes = AES.block_size  # 16

    @property
    def key(self):
        """
        key property accessor
        :return:
        """
        return self._key

    @key.setter
    def key(self, new_key: str):
        """
        key property mutator
        :param new_key:
        :return:
        """
        if len(bytes.fromhex(new_key)) != self.key_length_bytes:
            raise ValueError(
                f"key {new_key} is {len(bytes.fromhex(new_key))} bytes long\n"
                f"{self.key_length_bytes} bytes required\n"
            )
        self._key = new_key

    @property
    def iv(self):
        return self._iv

    @iv.setter
    def iv(self, new_iv: str):
        iv = (new_iv, self.create_salt())[new_iv is None]
        if len(bytes.fromhex(iv)) != self.iv_length_bytes:
            raise ValueError(
                f"`iv` {new_iv} is {len(bytes.fromhex(iv))} bytes long\n"
                f"{self.iv_length_bytes} bytes required\n"
            )
        self._iv = iv

    @property
    def salt(self):
        """
        salt property accessor
        :return:
        """
        # temporarily kick it to self._iv
        return self.iv

    def __init__(self, key: str, iv: Optional[str] = None, **kwargs):
        super(AesCtrIfc, self).__init__(key, iv, **kwargs)
        self.key = key
        # assigning None triggers creating new value; see iv.setter
        self.iv = iv
        return

    @property
    @abc.abstractmethod
    # This gets resolved by having a simple class attribute
    # Defining a classmethod property by decorators is needlessly complicated
    def key_length_bytes(self):
        """
        Required length in bytes of the encryption key
        @return: key_length_bytes
        @rtype: int
        """
        pass

    @classmethod
    def create_salt(cls):
        return secrets.token_hex(cls.iv_length_bytes)

    @property
    def cipher(self):
        """
        cipher property accessor; always returns a new one
        :return:
        """
        return AES.new(
            key=bytes.fromhex(self.key),
            mode=AES.MODE_CTR,
            counter=Counter.new(
                AES.block_size * 8,
                initial_value=int.from_bytes(
                    bytes.fromhex(self.iv), "big"
                )
            )
        )

    def encrypt(self, plaintext: str, iv: Optional[str] = None) -> str:
        if iv:
            self.iv = iv
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

    def decrypt(self, ciphertext: str, iv: Optional[str] = None) -> str:
        if iv:
            self.iv = iv
        # reverse the steps in `encrypt`
        # convert from str to bytes
        fs_safe_cipherbytes = ciphertext.encode('utf-8')
        # char substitution back to + and /
        cipherbytes = base64.urlsafe_b64decode(fs_safe_cipherbytes)
        # run the actual decryption
        plaintext_bytes = self.cipher.decrypt(cipherbytes)
        # convert the bytes to utf-8 str
        return plaintext_bytes.decode('utf-8')


class CryptAes128Ctr(AesCtrIfc):

    key_length_bytes = 16


class CryptAes256Ctr(AesCtrIfc):

    key_length_bytes = 32
