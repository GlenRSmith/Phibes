"""
Provides full encryption/hashing operations using
AES256 CTR-mode encryption and PBKDF2 hashing using SHA
"""

# Built-in library packages
import abc
import base64
import secrets
from typing import Optional

# Third party packages
from Cryptodome.Cipher import AES
from Cryptodome.Util import Counter

# In-project modules
from phibes.crypto.crypt_ifc import CryptIfc
from phibes.crypto.hash_pbkdf2 import HashPbkdf2


# TODO: revisit salt length. Only concern is if a chosen encryption
# implementation and hash implementation don't have a compatible
# length for salt.


class CryptAesCtrPbkdf2Sha(CryptIfc):
    """
    Crypt implementation for AES256 encryption with mode=Counter,
    with PBKDF2 key generation using SHA hashing

    Class composes
    - Pbkdf2 with SHA for crypt key generation & password hashing
    - AES counter-mode for encryption

    password + salt is hashed, hash is saved for auth
    password + salt is used to generate a crypt key
    crypt key + counter(iv=salt) are used to create a cipher
    For convenience, the same salt is used for each of these.
    """

    # No need to vary this, so not an instance value
    name_bytes = 4
    HashType = HashPbkdf2
    salt_length_bytes = AES.block_size  # 16

    @property
    @abc.abstractmethod
    def key_length_bytes(self):
        pass

    @key_length_bytes.setter
    @abc.abstractmethod
    def key_length_bytes(self, new_val: int):
        pass

    @classmethod
    def create_salt(cls):
        return secrets.token_hex(cls.salt_length_bytes)

    @property
    def cipher(self):
        """
        cipher property accessor; always returns a new one
        :return:
        """
        return AES.new(
            # key must be 16, 24 or 32 bytes long
            # respectively for *AES-128*, *AES-192* and *AES-256*.
            key=bytes.fromhex(self.key),
            mode=AES.MODE_CTR,
            counter=Counter.new(
                AES.block_size * 8,
                initial_value=int.from_bytes(
                    bytes.fromhex(self.iv), "big"
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
        return self.salt

    def __init__(
            self,
            crypt_id: str,
            password: str,
            pw_hash: Optional[str] = None,
            salt: Optional[str] = None,
            **kwargs
    ):
        self.key_rounds = kwargs.get('key_rounds')
        self.hash_rounds = self.key_rounds + 1
        super(CryptAesCtrPbkdf2Sha, self).__init__(
            crypt_id, password, pw_hash, salt, **kwargs
        )
        return

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

    def _hash_str(self, message, salt, rounds, length):
        return self._hasher.hash_str(
            message, salt=salt, rounds=rounds, length_bytes=length
        )

    def create_key(self, password: str, salt: str):
        return self._hash_str(
            password, salt, self.key_rounds,
            self.key_length_bytes
        )

    def hash_name(self, name: str, salt: Optional[str] = None) -> str:
        salt = (self.salt, salt)[bool(salt)]
        return self._hash_str(
            name, salt, self.hash_rounds, CryptAesCtrPbkdf2Sha.name_bytes
        )

    def __str__(self):
        return (
            f"{self.crypt_id=} - {type(self.crypt_id)=}"
            f"{self.salt=} - {type(self.salt)=}"
        )


class CryptAes128CtrPbkdf2Sha(CryptAesCtrPbkdf2Sha):
    """
    Crypt implementation for Counter-mode AES128 encryption
    """
    key_length_bytes = 16


class CryptAes192CtrPbkdf2Sha(CryptAesCtrPbkdf2Sha):
    """
    Crypt implementation for Counter-mode AES192 encryption
    """
    key_length_bytes = 24


class CryptAes256CtrPbkdf2Sha(CryptAesCtrPbkdf2Sha):
    """
    Crypt implementation for Counter-mode AES256 encryption
    """
    key_length_bytes = 32
