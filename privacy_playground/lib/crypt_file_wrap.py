"""
Cryptography support
"""

# Built-in library packages

from datetime import datetime
from pathlib import Path

# Third party packages

# In-project modules
from .crypto import make_crypt_key, make_salt_string
from .crypto import decrypt, encrypt


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
            raise FileNotFoundError(f"File {path.absolute()} does not exist")
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
