"""
Cryptography support
"""

# Built-in library packages
import base64
import hashlib
import secrets
from typing import Optional, Tuple

# Third party packages
from Cryptodome.Cipher import AES
from Cryptodome.Util import Counter

# In-project modules


HASH_ALGO = 'sha256'
CRYPT_KEY_ROUNDS = 100100
AUTH_KEY_ROUNDS = CRYPT_KEY_ROUNDS + 1
# PBKDF2-generated key length, default is 32 I think, longest AES allows
CRYPT_KEY_BYTES = 32
KEY_BYTES = 32
SALT_BYTES = AES.block_size  # 16
NAME_BYTES = 4

# HEX_REGEX = re.compile("^(0[xX])?[A-Fa-f0-9]+$")
# HexStr = Match[HEX_REGEX]
# KEY_REGEX = re.compile(b"[.]{CRYPT_KEY_BYTES}")
# KeyBytes = Match[KEY_REGEX]
# CipherDetails = Tuple[bytes, AES]


def make_salt_bytes(num_bytes: int = SALT_BYTES) -> bytes:
    return secrets.token_bytes(num_bytes)


def make_salt_string(num_bytes: int = SALT_BYTES):
    return make_salt_bytes(num_bytes).hex()


def encrypt(key: str, plaintext: str, iv: Optional[str] = None) -> str:
    """
    Encrypt some plaintext
    :param key: 32-byte encryption key
    :param plaintext: text to be encrypted, arbitrary length
    :param iv: initialization vector, optional, 16-bytes
    :return: iv, ciphertext
    """
    return CryptImpl(key, crypt_arg_is_key=True, salt=iv).encrypt(plaintext)


def decrypt(key: str, ciphertext: str, iv: str):
    """
    Decrypt a ciphertext
    :param key: 32-byte encryption key
    :param ciphertext: the encrypted text to decrypt
    :param iv: initialization vector, 16-bytes
    :return: plaintext from decryption
    """
    return CryptImpl(key, crypt_arg_is_key=True, salt=iv).decrypt(ciphertext)


def get_strong_hash(
        content: str,
        number_of_rounds: int,
        salt: str,
        length: int
) -> str:
    """
    Get a PDKDF2-based hash value for some string
    :param content: String to hash
    :param number_of_rounds: Number of rounds to iterate, integer
    :param salt: Hash salt, string containing valid hexadecimal
    :param length: Desired length of key in number of bytes
    :return: hash value, in bytes
    """
    # Library dependancy, so called function here *will* return bytes
    ret_val = hashlib.pbkdf2_hmac(
        HASH_ALGO, content.encode(), bytes.fromhex(salt),
        number_of_rounds, dklen=length
    )
    return ret_val.hex()


def make_crypt_key(seed: str, salt: str) -> str:
    """
    Convenience method to create a cryptographic key for the implemented
    encryption method
    :param seed: Starting string that will be hashed in round 1
    :param salt: String containing a hexadecimal value
    :return:
    """
    try:
        ret_val = get_strong_hash(
            seed, CRYPT_KEY_ROUNDS, salt, length=KEY_BYTES
        )
    except TypeError as err:
        raise err
    return ret_val


def get_password_hash(password: str, salt: str) -> str:
    """
    Convenience method to create a hash for a password using the implemented
    hashing method
    :param password: Password to be hashed
    :param salt: String containing a hexadecimal value
    :return:
    """
    try:
        ret_val = get_strong_hash(password, AUTH_KEY_ROUNDS, salt, length=KEY_BYTES)
    except TypeError as err:
        raise err
    return ret_val


def get_name_hash(name: str) -> str:
    """
    Return the one-way hash of the name.
    :param name:
    :return:
    """
    return get_strong_hash(name, AUTH_KEY_ROUNDS, '0000', length=NAME_BYTES)


class CryptImpl(object):

    def __init__(
            self,
            crypt_arg: str,
            crypt_arg_is_key: bool = True,
            salt: str = make_salt_string()
    ):
        salt = (make_salt_string(), salt)[bool(salt)]
        self.salt = salt
        if crypt_arg_is_key:
            self.key = crypt_arg
        else:
            self.key = make_crypt_key(crypt_arg, salt)
        self._refresh_cipher(salt)
        return

    def encrypt(self, plaintext: str) -> str:
        cipherbytes = self.cipher.encrypt(plaintext.encode('utf-8'))
        ret_val = base64.urlsafe_b64encode(cipherbytes).decode('utf-8')
        self._refresh_cipher(self.salt)
        return ret_val

    def decrypt(self, ciphertext: str) -> str:
        cipherbytes = base64.urlsafe_b64decode(ciphertext)
        ret_val = self.cipher.decrypt(cipherbytes).decode()
        self._refresh_cipher(self.salt)
        return ret_val

    def encrypt_password(self, password: str) -> str:
        return encrypt(
            self.key,
            get_password_hash(password, self.salt),
            self.salt
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
        key_bytes = bytes.fromhex(self.key)
        if not len(key_bytes) == CRYPT_KEY_BYTES:
            raise ValueError(
                f"`key` arg must be exactly {CRYPT_KEY_BYTES} long\n"
                f"{key_bytes} (from key:{self.key}) is {len(key_bytes)}"
            )
        self.cipher = AES.new(
            key=key_bytes,
            mode=AES.MODE_CTR,
            counter=Counter.new(
                AES.block_size * 8,
                initial_value=int.from_bytes(bytes.fromhex(salt), "big")
            )
        )
        return

    def __str__(self):
        return (
            f"key: {self.key} - type: {type(self.key)}\n"
            f"iv: {self.salt} - type: {type(self.salt)}"
        )
