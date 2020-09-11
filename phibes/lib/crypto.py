"""
Cryptography support
"""

# Built-in library packages
import abc
import base64
import hashlib
from pathlib import Path
import secrets
from typing import Optional

# Third party packages
from Cryptodome.Cipher import AES
from Cryptodome.Util import Counter

# In-project modules
from phibes.crypto.crypt_ifc import CryptIfc


current_crypt_config = {
    "hash_algo": "sha256",
    "crypt_key_rounds": 100100,
    "auth_key_rounds": 100101,
    "key_bytes": 32,  # 256 bits
    "salt_bytes": 16,  # AES.block_size
    "name_bytes": 4,
    "mode": AES.MODE_CTR,
    "AES": {"mode": "MODE_CTR"}
}

available_versions = {
    "current": current_crypt_config
}


def get_crypt_version(version="current"):
    return available_versions.get(version)


def get_strong_hash(
        content: str,
        number_of_rounds: int,
        salt: str,
        length: int,
        hash_algo
) -> str:
    """
    Get a PDKDF2-based hash value for some string
    :param content: String to hash
    :param number_of_rounds: Number of rounds to iterate, integer
    :param salt: Hash salt, string containing valid hexadecimal
    :param length: Desired length of key in number of bytes
    :param hash_algo: Hash algorithm for hmac to use
    :return: hash value, in bytes
    """
    # Library dependency, so called function here *will* return bytes
    ret_val = hashlib.pbkdf2_hmac(
        hash_algo, content.encode(), bytes.fromhex(salt),
        number_of_rounds, dklen=length
    )
    return ret_val.hex()


def get_name_hash(name: str, version: Optional[str] = "current") -> str:
    """
    Return the one-way hash of the name.

    Uses the same hash method as used in encryption, but wouldn't have to.
    @param name: plaintext name string
    @type name: str
    @param version: affordance for future change of encryption/hash methods
    @type version: str
    @return: hashed result
    @rtype: str
    """
    ccv = get_crypt_version(version)
    return hashlib.pbkdf2_hmac(
        ccv.get("hash_algo"),
        name.encode(),
        bytes.fromhex('0000'),
        ccv.get("auth_key_rounds"),
        dklen=ccv.get("name_bytes")
    ).hex()


class CryptImpl(CryptIfc):

    @property
    def salt(self):
        """
        salt property accessor
        :return:
        """
        return self._salt

    @salt.setter
    def salt(self, new_salt: str):
        """
        salt property mutator
        :param new_salt:
        :return:
        """
        self._salt = new_salt
        self._refresh_cipher(new_salt)
        return

    def __init__(
            self,
            password: str,
            salt: Optional[str] = None,
            version: Optional[str] = "current"
    ):
        super(CryptImpl, self).__init__(password, salt)
        ccv = get_crypt_version(version)
        self.salt_len = ccv.get("salt_bytes")
        self.rounds = ccv.get("crypt_key_rounds")
        self.key_bytes = ccv.get("key_bytes")
        self.name_bytes = ccv.get("name_bytes")
        self.hash_algo = ccv.get("hash_algo")
        self.aes_mode = getattr(AES, ccv.get("AES").get("mode"))
        if salt:
            # `len` is character length, twice byte length
            if len(salt) != self.salt_len * 2:
                raise ValueError(
                    f"salt must be {self.salt_len} bytes long\n"
                    f"{salt} is {len(salt)/2} bytes long"
                )
        else:
            salt = secrets.token_hex(self.salt_len)
        self._salt = salt
        try:
            self.key = get_strong_hash(
                password,
                self.rounds,
                salt,
                self.key_bytes,
                self.hash_algo
            )
        except TypeError as err:
            raise err
        self._refresh_cipher(salt)
        return

    def encrypt(self, plaintext: str) -> str:
        # convert from str to bytes
        plaintext_bytes = plaintext.encode('utf-8')
        # run the actual encryption - it gets bytes, returns bytes
        cipherbytes = self.cipher.encrypt(plaintext_bytes)
        # substitute for chars that aren't file-system safe
        # e.g. - instead of + and _ instead of /
        # it gets bytes, returns bytes
        fs_safe_cipherbytes = base64.urlsafe_b64encode(cipherbytes)
        # convert the bytes to a utf-8 str
        ret_val = fs_safe_cipherbytes.decode('utf-8')
        self._refresh_cipher(self._salt)
        return ret_val

    def decrypt(self, ciphertext: str) -> str:
        # reverse the steps in `encrypt`
        # convert from str to bytes
        fs_safe_cipherbytes = ciphertext.encode('utf-8')
        # char substitution back to + and /
        cipherbytes = base64.urlsafe_b64decode(fs_safe_cipherbytes)
        # run the actual decryption
        plaintext_bytes = self.cipher.decrypt(cipherbytes)
        # convert the bytes to utf-8 str
        ret_val = plaintext_bytes.decode('utf-8')
        self._refresh_cipher(self.salt)
        return ret_val

    def strong_hash(self, plaintext: str, salt: str, length: int) -> str:
        # Library dependency, so called function here *will* return bytes
        ret_val = hashlib.pbkdf2_hmac(
            self.hash_algo, plaintext.encode(), bytes.fromhex(salt),
            self.rounds, dklen=length
        )
        return hashlib.pbkdf2_hmac(
            self.hash_algo,
            plaintext.encode(),
            bytes.fromhex(salt),
            self.rounds,
            dklen=self.name_bytes
        ).hex()

    def encrypt_password(self, password: str) -> str:
        """
        Performs a hash on the password, then encrypts the hash
        @param password: password to encrypt
        @type password: str
        @return: encrypted value
        @rtype: str
        """
        return self.encrypt(
            get_strong_hash(
                password,
                self.rounds,
                self.salt,
                length=self.key_bytes,
                hash_algo=self.hash_algo
            )
        )

    def authenticate(self, password: str, cipher: str):
        """
        Run the submitted password through the same hash+encryption
        that produced the cipher, and compare
        :param password: Submitted password
        :param cipher: The canonical hash, encrypted value
        :return:
        """
        return cipher == self.encrypt_password(password)

    def _refresh_cipher(self, salt: str):
        """
        Create a new cipher instance - least complicated way to
        avoid exceptions like "can't encrypt after decrypt" and vice-versa
        :param salt:
        :return:
        """
        self.cipher = AES.new(
            key=bytes.fromhex(self.key),
            mode=AES.MODE_CTR,
            # mode=self.aes_mode,
            counter=Counter.new(
                AES.block_size * 8,
                initial_value=int.from_bytes(
                    bytes.fromhex(salt), "big"
                )
            )
        )
        return

    def __str__(self):
        return (
            f"key: {self.key} - type: {type(self.key)}\n"
            f"iv: {self.salt} - type: {type(self.salt)}"
        )


def new_get_name_hash(crypt_obj: CryptIfc, name: str):
    return crypt_obj.strong_hash(name, '0000', 4)
