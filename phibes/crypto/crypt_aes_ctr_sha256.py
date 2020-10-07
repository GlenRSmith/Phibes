"""
Provides full encryption/hashing operations using
AES256 CTR-mode encryption and PBKDF2 hashing using SHA
"""

# Built-in library packages
from typing import Optional

# Third party packages

# In-project modules
from phibes.crypto.crypt_ifc import CryptIfc
from phibes.crypto.hash_pbkdf2 import HashPbkdf2
from phibes.crypto.encrypt_aes import CryptAes256Ctr


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
    EncryptType = CryptAes256Ctr

    @property
    def salt(self):
        """
        salt property accessor
        :return:
        """
        return self._encrypt.salt

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

    def encrypt(self, plaintext: str, salt: Optional[str] = None) -> str:
        return self._encrypt.encrypt(plaintext, salt)

    def decrypt(self, ciphertext: str, salt: Optional[str] = None) -> str:
        return self._encrypt.decrypt(ciphertext, salt)

    def _hash_str(self, message, salt, rounds, length):
        return self._hasher.hash_str(
            message, salt=salt, rounds=rounds, length_bytes=length
        )

    def create_key(self, password: str, salt: str):
        return self._hash_str(
            password, salt, self.key_rounds, CryptAes256Ctr.key_length_bytes
        )

    def hash_name(self, name: str, salt: Optional[str] = '0000') -> str:
        return self._hash_str(
            name, salt, self.hash_rounds, CryptAesCtrPbkdf2Sha.name_bytes
        )

    def __str__(self):
        return (
            f"{self.crypt_id=} - {type(self.crypt_id)=}"
            f"{self.salt=} - {type(self.salt)=}"
        )
