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
from pathlib import Path
import secrets

# Third party packages
from Cryptodome.Cipher import AES
from Cryptodome.Util import Counter

# In-project modules
from lib.config import LOCKER_PATH

HASH_ALGO = 'sha256'
CRYPT_KEY_ROUNDS = 100100
AUTH_KEY_ROUNDS = CRYPT_KEY_ROUNDS + 1
CRYPT_KEY_BYTES = 32
KEY_BYTES = 32
SALT_BYTES = 16
# PBKDF2-generate key length, default is 32 I think, longest AES allows


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
    cipherbytes = base64.urlsafe_b64decode(ciphertext)
    return cipher.decrypt(cipherbytes)


def get_strong_hash(content, number_of_rounds, salt):
    """
    Get a PDKDF2-based hash value for some string
    :param content: String to hash, string
    :param number_of_rounds: Number of rounds to iterate, integer
    :param salt: Hash salt, string containing valid hexadecimal
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


# def manage_file(func):
#
#     def wrapped_handler(*args, **kwargs):
#         print(f"{func.__name__}")
#         print(f"{args}{kwargs}")
#         return func(*args, **kwargs)
#     return wrapped_handler


class Secret(object):

    def __init__(self, name, locker, create=False):
        # locker_path =
        self.name = name
        self.locker = locker
        self.salt = None
        self.ciphertext = None
        self.secret_name = None
        # don't want to even expose the plaintext name
        self.secret_name = self.locker.encrypt(self.name)
        self.secret_file = os.path.join(
            locker.locker_path, f"{self.secret_name}.sct"
        )
        if os.path.exists(self.secret_file):
            pass
        super().__init__()  # is this best practice?

    def validate(self):
        return

    def create(self, secret_text):
        # safely get random bytes, turn into string hexadecimal
        self.salt = secrets.token_bytes(SALT_BYTES).hex()
        iv, self.ciphertext = encrypt(
            self.locker.crypt_key, secret_text, iv=bytes.fromhex(self.salt)
        )
        # Write the new Secret file
        entry = f"{self.salt}\n{self.ciphertext}\n"
        with open(self.secret_file, "w") as cipher_file:
            cipher_file.write(entry)
        return

    def read(self):
        self.validate()
        with open(f"{self.secret_file}", "r") as s_file:
            # the salt was stored in hexadecimal form, with a line feed
            self.salt = s_file.readline().strip('\n')
            # the next line in the file is the encrypted secret
            read_secret = s_file.readline().strip('\n')
            ciphertext = decrypt(
                self.locker.crypt_key, bytes.fromhex(self.salt), read_secret
            )
        return ciphertext.decode()


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
        # crypt_key will be the symmetrical encryption key
        # It is derived from the main password, but wouldn't have to be.
        self.crypt_key = None
        self.salt = None

        # Make sure the application's base locker path is an existing dir
        base_path = Path(LOCKER_PATH)
        if not base_path.exists():
            os.mkdir(LOCKER_PATH)
        if not base_path.is_dir():
            raise ValueError(f"Base path {LOCKER_PATH} is not a directory")

        # Locker will be a directory and have a file for salt and auth hash
        self.locker_path = base_path.joinpath(name)
        self.lock_file = self.locker_path.joinpath(".locker.cfg")
        if create:
            if Locker.can_create(self.locker_path):
                os.mkdir(self.locker_path)
                # safely get random bytes, turn into string hexadecimal
                self.salt = secrets.token_bytes(16).hex()
                # create a crypt key from the password - never store that!
                self.crypt_key = get_crypt_key(password, self.salt)
                # iv, self.auth_hash = encrypt(
                iv, auth_hash = encrypt(
                    self.crypt_key,
                    get_password_hash(password, self.salt).hex(),
                    iv=bytes.fromhex(self.salt)
                )
                with open(self.lock_file, "w") as vault_file:
                    vault_file.write(f"{self.salt}\n{auth_hash}\n")
                    # vault_file.write(f"{self.salt}\n{self.auth_hash}\n")
            else:
                raise ValueError(f"could not create {name}")
        else:
            with open(f"{self.lock_file}", "r") as locker_file:
                # the salt was stored in hexadecimal form, with a line feed
                self.salt = locker_file.readline().strip('\n')
                # the next line is the encrypted hash of the secret
                auth_hash = locker_file.readline().strip('\n')
                # calculate a key from the password submitted for auth
                self.crypt_key = get_crypt_key(password, self.salt)
                # try to decrypt using that key
                passhash = decrypt(
                    self.crypt_key, bytes.fromhex(self.salt), auth_hash
                )
                # Calculate the hash of the password
                passhash2 = get_password_hash(password, self.salt)
                # Compare the values to validate presented password
                if passhash2.hex() != passhash.decode():
                    raise ValueError(
                        f"{passhash2.hex()} & {passhash.decode()} don't match"
                    )

        super().__init__()  # is this best practice?

    @classmethod
    def can_create(cls, locker_path):
        """
        Evaluates whether the filesystem allows creation of a new locker
        :return: Bool
        """
        if locker_path.exists():
            if not locker_path.is_dir():
                raise ValueError(
                    f"{locker_path} already exists and is not a directory"
                )
            if bool(locker_path.glob('*')):
                raise ValueError(
                    f"dir {locker_path} already exists and is not empty"
                )
        return True

    def validate(self):
        if not os.path.exists(self.locker_path):
            raise ValueError(f"Locker path {self.locker_path} does not exist")
        if not os.path.isdir(self.locker_path):
            raise ValueError(f"Locker path {self.locker_path} not a directory")
        if not os.path.exists(self.lock_file):
            raise ValueError(f"Locker file {self.lock_file} does not exist")
        if not os.path.isfile(self.lock_file):
            raise ValueError(f"{self.lock_file} is not a file")

    def _open(self, pw):
        self.validate()
        with open(f"{self.lock_file}", "r") as locker_file:
            # the salt was stored in hexadecimal form, with a line feed
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

    def _delete(self, pw):
        self.validate()
        with open(f"{self.lock_file}", "r") as locker_file:
            # the salt was stored in hexadecimal form, with a line feed
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

    def decrypt(self, ciphertext):
        """
        Convenience method to decrypt using a Locker object
        :param ciphertext: Encrypted text
        :return: decrypted text
        """
        return decrypt(
            self.crypt_key, bytes.fromhex(self.salt), ciphertext
        )

    def encrypt(self, plaintext):
        """
        Convenience method to encrypt using a Locker object
        :param plaintext: Text to encrypt
        :return: encrypted text
        """
        iv, ciphertext = encrypt(
            self.crypt_key, plaintext, iv=bytes.fromhex(self.salt)
        )
        return ciphertext

    def list_secrets(self):
        self.validate()
        secret_names = []
        for entry in os.scandir(self.locker_path):
            if entry.is_file() and entry.name.endswith('.sct'):
                secret_names.append(
                    self.decrypt(entry.name[0:-4]).decode()
                )
        return secret_names

