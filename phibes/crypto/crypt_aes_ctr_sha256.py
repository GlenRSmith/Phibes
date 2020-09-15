"""
Provides full encryption/hashing operations using
AES256 CTR-mode encryption and PBKDF2 hashing using SHA256
"""

# Built-in library packages
from typing import Optional

# Third party packages

# In-project modules
from phibes.crypto.crypt_ifc import CryptIfc
from phibes.crypto.hash_pbkdf2 import HashPbkdf2
from phibes.crypto.encrypt_aes import CryptAes256Ctr
from phibes.lib.errors import PhibesAuthError


# TODO: revisit salt length. Only concern is if a chosen encryption
# implementation and hash implementation don't have a compatible
# length for salt.


class CryptAesCtrPbkdf2Sha(CryptIfc):
    """
    Crypt implementation for AES256 encryption with mode=Counter,
    with PBKDF2 key generation using SHA256 hashing

    Class composes
    - Pbkdf2 with SHA256 for crypt key generation
    - Pbkdf2 with SHA256 for password hashing
    - AES counter-mode for encryption

    password + salt is hashed, hash is saved for auth
    password + salt is used to generate a crypt key
    crypt key + counter(iv=salt) are used to create a cipher
    For convenience, the same salt is used for each of these.
    """

    # No need to vary this, so not an instance value
    name_bytes = 4

    @property
    def salt(self):
        """
        salt property accessor
        :return:
        """
        return self._encrypt.salt

    def __init__(
        self,
        password: str,
        pw_hash: Optional[str] = None,
        salt: Optional[str] = None,
        **kwargs: dict
    ):
        super(CryptAesCtrPbkdf2Sha, self).__init__(
            password, pw_hash, salt, **kwargs
        )
        self.key_rounds = kwargs.get('key_rounds')
        self.hash_alg = kwargs.get('hash_alg')
        self.hash_rounds = self.key_rounds + 1
        creating = password and not pw_hash and not salt
        if not (password and pw_hash and salt) and not creating:
            pref = f"{self.__class__.__name__}\n"
            raise ValueError(
                f"invalid call to __init__\n"
                f"valid calls are are:\n"
                f"{pref}(password, key_rounds=<int>)\n"
                f"{pref}(password, pw_hash, salt, key_rounds=int)\n"
                f"{password=} {pw_hash=} {salt=} {kwargs=}"
            )
        self._hasher = HashPbkdf2(**{'hash_alg': self.hash_alg})
        if creating:
            salt = CryptAes256Ctr.create_salt()
        try:
            key = self.create_key(password, salt)
            self._encrypt = CryptAes256Ctr(key, salt)
            auth_key = self.encrypt(self.hash_name(password, salt))
            if not creating:
                if not auth_key == pw_hash:
                    raise PhibesAuthError(
                        f"{pw_hash} does not match {auth_key}"
                    )
            self.pw_hash = auth_key

        except TypeError as err:
            raise err
        return

    def encrypt(self, plaintext: str, salt: Optional[str] = None) -> str:
        return self._encrypt.encrypt(plaintext, salt)

    def decrypt(self, ciphertext: str, salt: Optional[str] = None) -> str:
        return self._encrypt.decrypt(ciphertext, salt)

    def _hash_str(self, message, salt, rounds, length):
        return self._hasher.hash_str(message, salt, rounds, length)

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
