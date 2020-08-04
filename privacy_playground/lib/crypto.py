"""
Cryptography support
"""

# Built-in library packages
import base64
import hashlib
import secrets

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
SALT_BYTES = 16
NAME_BYTES = 4


def make_salt_string(num_bytes=SALT_BYTES):
    return secrets.token_bytes(num_bytes).hex()


def make_salt_bytes(num_bytes=SALT_BYTES):
    return secrets.token_bytes(num_bytes)


def get_cipher(key, iv=None):
    assert len(key) == CRYPT_KEY_BYTES
    if not iv:
        iv = secrets.token_bytes(AES.block_size)
    iv_int = int.from_bytes(iv, "big")
    ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    return iv, cipher


def encrypt(key, plaintext, iv=None):
    """
    Encrypt some plaintext
    :param key: 32-byte encryption key
    :param plaintext: text to be encrypted, arbitrary length
    :param iv: initialization vector, optional, 16-bytes
    :return: iv, ciphertext
    """
    iv, cipher = get_cipher(key, iv=iv)
    cipherbytes = cipher.encrypt(plaintext.encode('utf-8'))
    ciphertext = base64.urlsafe_b64encode(cipherbytes).decode('utf-8')
    return iv, ciphertext


def decrypt(key, iv, ciphertext):
    """
    Decrypt a ciphertext
    :param key: 32-byte encryption key
    :param iv: initialization vector, 16-bytes
    :param ciphertext: the encrypted text to decrypt
    :return: plaintext from decryption
    """
    iv, cipher = get_cipher(key, iv=iv)
    cipherbytes = base64.urlsafe_b64decode(ciphertext)
    return cipher.decrypt(cipherbytes)


def get_strong_hash(
        content: str,
        number_of_rounds: int,
        salt: str,
        length: int
) -> bytes:
    """
    Get a PDKDF2-based hash value for some string
    :param content: String to hash
    :param number_of_rounds: Number of rounds to iterate, integer
    :param salt: Hash salt, string containing valid hexadecimal
    :param length: Desired length of key in number of bytes
    :return: hash value, in bytes
    """
    ret_val = hashlib.pbkdf2_hmac(
        HASH_ALGO, content.encode('utf-8'), bytes.fromhex(salt),
        number_of_rounds, dklen=length
    )
    return ret_val


def make_crypt_key(seed: str, salt: str) -> bytes:
    """
    Convenience method to create a cryptographic key for the implemented
    encryption method
    :param seed: Starting string that will be hashed in round 1
    :param salt: String containing a hexadecimal value
    :return:
    """
    return get_strong_hash(seed, CRYPT_KEY_ROUNDS, salt, length=KEY_BYTES)


def get_password_hash(password: str, salt: str) -> bytes:
    """
    Convenience method to create a hash for a password using the implemented
    hashing method
    :param password: Password to be hashed
    :param salt: String containing a hexadecimal value
    :return:
    """
    return get_strong_hash(password, AUTH_KEY_ROUNDS, salt, length=KEY_BYTES)


def authenticate_password(password: str, cipher: str, salt: str):
    """
    Run the submitted password through the same hash+encryption
    that producted the cipher, and compare
    :param password: Submitted password
    :param cipher: The canonical hash, encrypted value
    :param salt: Crypto salt, a hexadecimal value
    :return:
    """
    salt_back, ciphertext = encrypt(
        make_crypt_key(password, salt),
        get_password_hash(password, salt).hex(),
        bytes.fromhex(salt)
    )
    if cipher != ciphertext:
        raise ValueError(
            f"{cipher} & {ciphertext} don't match"
        )
    return True


def get_name_hash(name):
    """
    Return the one-way hash of the name.
    :param name:
    :return:
    """
    return get_strong_hash(
        name, AUTH_KEY_ROUNDS, '0000', length=NAME_BYTES
    ).hex()
