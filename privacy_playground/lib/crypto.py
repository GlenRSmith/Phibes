"""
Cryptography support
"""

# Built-in library packages
import base64
from datetime import datetime
import hashlib
from pathlib import Path
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


class CryptFileWrap(object):
    """
    Class for access to files with encrypted content in a standard form
    line 1: cryptographic salt
    line 2: timestamp of most recent write
    line 3: encrypted content

    The salt is unique for every file.

    In a Locker file, the "content" is the password hash.
    Not the password, but the password hash.
    With the correct password and the salt from the file,
    the correct cryptographic key can be generated.

    In the case of an Item file, the content is whatever the user saves.
    The key required is the key from the Locker owning the Item.
    """

    def __init__(self, path: Path):
        """
        :param path:
        """
        self.path = path
        self.salt = None
        self.key = None
        self._timestamp = None
        self._ciphertext = None
        return

    def delete(self):
        if not self.path.exists():
            raise FileNotFoundError(f"{self.path} does not exist")
        self.path.unlink()

    @classmethod
    def create(cls, path: Path, crypt_arg, crypt_arg_is_key: bool):
        """
        Create (but don't save yet) an instance.
        If crypt_arg_is_key, caller already has an encryption key.
        Otherwise, caller is passing in a "seed" (like password I'm using)
        :param path: encryption file location
        :param crypt_arg: crypt key or password
        :param crypt_arg_is_key: whether crypt_arg is a crypt key, o/w password
        :return:
        """
        if path.exists():
            raise FileExistsError(f"{path} already exists")
        inst = cls(path)
        inst.salt = make_salt_string()
        if crypt_arg_is_key:
            inst.key = crypt_arg
        else:
            inst.key = make_crypt_key(crypt_arg, inst.salt)
        return inst

    @classmethod
    def find(cls, path):
        """
        Tries to get, read, and return conformant file at the path
        :param path:
        :return: class instance
        """
        if not path.exists():
            raise FileNotFoundError(f"File {path} does not exist")
        with path.open('r') as cf:
            # the salt was stored as a hexadecimal string
            salt = cf.readline().strip('\n')
            # the next line is an encrypted datetime stamp
            timestamp = cf.readline().strip('\n')
            # the next line is the encrypted content
            ciphertext = cf.readline().strip('\n')
        # If those reads succeeded, create & populate an object instance
        inst = cls(path)
        inst.salt = salt
        inst._ciphertext = ciphertext
        inst._timestamp = timestamp
        return inst

    @property
    def plaintext(self):
        """
        Plaintext only available here by decrypting
        :return:
        """
        return decrypt(
            self.key, bytes.fromhex(self.salt), self._ciphertext
        ).decode()

    @plaintext.setter
    def plaintext(self, content: str):
        """
        Take the submitted plaintext and update the ciphertext attribute,
        as well as the the salt used to encrypt
        :param content:
        :return:
        """
        if not self.salt:
            raise ValueError(f"salt has not been set on CryptFileWrapper")
        extra_iv, self._ciphertext = encrypt(
            self.key, content, iv=bytes.fromhex(self.salt)
        )
        return

    @property
    def timestamp(self):
        return decrypt(
            self.key, bytes.fromhex(self.salt), self._timestamp
        ).decode()

    @property
    def ciphertext(self):
        return self._ciphertext

    def set_crypt_key(self, password):
        self.key = make_crypt_key(password, self.salt)

    def read(self):
        # TODO: might be redundant
        if not self.path.exists():
            raise FileExistsError(f"File {self.path} does not exist")
        with self.path.open('r') as cf:
            # the salt was stored in hexadecimal form, with a line feed
            self.salt = cf.readline().strip('\n')
            # the next line in the file is a datetime stamp
            self._timestamp = cf.readline().strip('\n')
            # the next line in the file is the encrypted content
            self._ciphertext = cf.readline().strip('\n')
        return

    def write(self, overwrite=False):
        if self.path.exists() and not overwrite:
            raise FileExistsError(
                f"file {self.path} already exists, and overwrite is False"
            )
        elif self._ciphertext is None:
            raise AttributeError(f"Item has no content!")
        else:
            self._timestamp = str(datetime.now())
            salt_back, ts = encrypt(
                self.key, self._timestamp, iv=bytes.fromhex(self.salt)
            )
            item = f"{self.salt}\n{ts}\n{self._ciphertext}\n"
            with self.path.open("w") as cipher_file:
                cipher_file.write(item)
        return
