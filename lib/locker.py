"""
A Locker is a storage unit for user secrets (passwords, etc.)
A Locker is represented by a file "<name>.lck" on the local file system.
A Locker has other data on the file system, but that file
(which contains the single access credentials) is the requisite bit.
"""

# Built-in library packages
import base64
import hashlib
import os
import secrets

# Third party packages
from Cryptodome.Cipher import AES
from Cryptodome.Util import Counter

# In-project modules

HASH_ALGO = 'sha256'
CRYPT_KEY_ROUNDS = 100100
AUTH_KEY_ROUNDS = CRYPT_KEY_ROUNDS + 1
CRYPT_KEY_BYTES = 32
KEY_BYTES = 32
# PBKDF2-generate key length, default is 32 I think, longest AES allows
LOCKER_PATH = "locker"


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
    ciphertext = base64.b64encode(cipherbytes).decode('utf-8')
    return iv, ciphertext


# Takes as input a 32-byte key, a 16-byte IV, and a ciphertext, and returns the
# corresponding plaintext.
def decrypt(key, iv, ciphertext):
    """
    Decrypt a ciphertext
    :param key: 32-byte encryption key
    :param iv: initialization vector, 16-bytes
    :param ciphertext: the encrypted text to decrypt
    :return: plaintext from decryption
    """
    iv, cipher = get_cipher(key, iv=iv)
    cipherbytes = base64.b64decode(ciphertext)
    return cipher.decrypt(cipherbytes)


def get_strong_hash(content, number_of_rounds, salt):
    """
    Get a PDKDF2-based hash value for some string
    :param content: String to hash, string
    :param number_of_rounds: Number of rounds to iterate, integer
    :param salt: Hash salt, string containing valid hexidecimal
    :return: hash value, in bytes
    """
    ret_val = hashlib.pbkdf2_hmac(
        HASH_ALGO,
        content.encode('utf-8'),
        bytes.fromhex(salt),
        number_of_rounds,
        dklen=KEY_BYTES
    )
    return ret_val


def get_crypt_key(seed, salt):
    return get_strong_hash(seed, CRYPT_KEY_ROUNDS, salt)


def get_password_hash(password, salt):
    return get_strong_hash(password, AUTH_KEY_ROUNDS, salt)


class Locker(object):

    def __init__(self, name, password, create=False):
        """
        A Locker object can be constructed in two scenarios:
        - client code is creating a new, empty locker
          - this method should create the locker on disk
        - client code is opening an interface to an existing locker
          - this method should try to open the locker on disk
        :param name: The name of the locker. Must be unique in storage
        :param password: The password to the locker
        :param create: Should invocation try to create a new locker?
        """
        # Try to find an existing locker. Even if we get the `create` flag,
        # we will need to guard against accidental overwriting
        self.auth_hash = None
        # auth_hash will be the hash used to auth the user
        # It is derived from the main password.
        self.crypt_key = None
        # crypt_key will be the symmetrical encryption key
        # It is derived from the main password, but wouldn't have to be.
        self.salt = None
        lock_file = os.path.join(LOCKER_PATH, f"{name}.lck")
        exists = os.path.exists(lock_file)
        isfile = os.path.isfile(lock_file)
        if exists:
            if not isfile:
                raise SyntaxError(f"{lock_file} exists and isn't a file")
            else:
                if create:
                    raise SyntaxError(f"{lock_file} already exists!")
                else:
                    self._open(name, password)
        else:
            self._create(name, password)
        super().__init__()  # is this best practice?

    def _create(self, name, password):
        # safely get random bytes, turn into string hexadecimal
        self.salt = secrets.token_bytes(16).hex()
        # create a crypt key from the password - never store that!
        self.crypt_key = get_crypt_key(password, self.salt)
        self.auth_hash = get_password_hash(password, self.salt).hex()
        # Encrypt the password hash before storing it
        iv, self.auth_hash = encrypt(
            self.crypt_key, self.auth_hash, iv=bytes.fromhex(self.salt)
        )
        # Write the new locker file
        entry = f"{self.salt}\n{self.auth_hash}\n"
        lock_file = os.path.join(LOCKER_PATH, f"{name}.lck")
        with open(lock_file, "w") as vault_file:
            vault_file.write(entry)
        return

    def _open(self, name, pw):
        lock_file = os.path.join(LOCKER_PATH, f"{name}.lck")
        with open(f"{lock_file}", "r") as locker_file:
            # the salt was stored in hexidecimal form, with a line feed
            self.salt = locker_file.readline().strip('\n')
            # the next line in the file is the encrypted hash of the pw with lf
            read_hash_hash = locker_file.readline().strip('\n')
            # calculate the hypothetical key based on the pw submitted for auth
            self.crypt_key = get_crypt_key(pw, self.salt)
            # try to decrypt using the presented password's key
            passhash = decrypt(
                self.crypt_key, bytes.fromhex(self.salt), read_hash_hash
            )
            passhash2 = get_password_hash(pw, self.salt)
            # Compare the values to validate presented password
            if passhash2.hex() != passhash.decode():
                raise ValueError(
                    f"{passhash2.hex()} and {passhash.decode()} do not match"
                )
        return self.salt, read_hash_hash
