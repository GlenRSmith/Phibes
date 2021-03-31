"""
Provides full encryption/hashing operations using
AES256 CTR-mode encryption and PBKDF2 hashing using SHA
"""

# Built-in library packages
import abc
import secrets
from typing import Optional

# Third party packages
from Cryptodome.Cipher import AES

# In-project modules
from phibes.crypto import aes_cipher
from phibes.crypto.crypt_ifc import CryptIfc
from phibes.crypto.hash_pbkdf2 import pbkdf2


# TODO: revisit salt length. Only concern is if a chosen encryption
# implementation and hash implementation don't have a compatible
# length for salt.


class AesCtrPbkdf2Sha(CryptIfc):
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
    salt_length_bytes = AES.block_size  # 16

    @property
    @abc.abstractmethod
    def key_length_bytes(self):
        pass

    @key_length_bytes.setter
    @abc.abstractmethod
    def key_length_bytes(self, new_val: int):
        pass

    @property
    @abc.abstractmethod
    def hash_alg(self):
        pass

    @hash_alg.setter
    @abc.abstractmethod
    def hash_alg(self, new_val: int):
        pass

    @classmethod
    def create_salt(cls):
        return secrets.token_hex(cls.salt_length_bytes)

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
        super(AesCtrPbkdf2Sha, self).__init__(
            crypt_id, password, pw_hash, salt, hash_alg=self.hash_alg, **kwargs
        )
        return

    def encrypt(self, plaintext: str) -> str:
        return aes_cipher.encrypt(self.key, self.iv, plaintext)

    def decrypt(self, ciphertext: str) -> str:
        return aes_cipher.decrypt(self.key, self.iv, ciphertext)

    def create_key(self, password: str, salt: str):
        return pbkdf2(
            self.hash_alg,
            password,
            salt,
            self.key_rounds,
            self.key_length_bytes
        )

    def hash_name(self, name: str, salt: str) -> str:
        return pbkdf2(
            self.hash_alg,
            name,
            salt,
            self.hash_rounds,
            self.name_bytes
        )

    def __str__(self):
        return (
            f"{self.crypt_id=} - {type(self.crypt_id)=}"
            f"{self.salt=} - {type(self.salt)=}"
        )


class Aes128CtrPbkdf2Sha256(AesCtrPbkdf2Sha):
    """
    Crypt implementation for Counter-mode AES128 encryption
    with key generation using SHA256
    """
    key_length_bytes = 16
    hash_alg = 'SHA256'


class Aes128CtrPbkdf2Sha512(AesCtrPbkdf2Sha):
    """
    Crypt implementation for Counter-mode AES128 encryption
    with key generation using SHA512
    """
    key_length_bytes = 16
    hash_alg = 'SHA512'


class Aes192CtrPbkdf2Sha256(AesCtrPbkdf2Sha):
    """
    Crypt implementation for Counter-mode AES192 encryption
    with key generation using SHA256
    """
    key_length_bytes = 24
    hash_alg = 'SHA256'


class Aes192CtrPbkdf2Sha512(AesCtrPbkdf2Sha):
    """
    Crypt implementation for Counter-mode AES192 encryption
    with key generation using SHA512
    """
    key_length_bytes = 24
    hash_alg = 'SHA512'


class Aes256CtrPbkdf2Sha256(AesCtrPbkdf2Sha):
    """
    Crypt implementation for Counter-mode AES256 encryption
    with key generation using SHA256
    """
    key_length_bytes = 32
    hash_alg = 'SHA256'


class Aes256CtrPbkdf2Sha512(AesCtrPbkdf2Sha):
    """
    Crypt implementation for Counter-mode AES256 encryption
    with key generation using SHA512
    """
    key_length_bytes = 32
    hash_alg = 'SHA512'
