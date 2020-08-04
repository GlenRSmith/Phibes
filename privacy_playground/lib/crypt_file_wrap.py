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

    def __init__(
            self, path: Path,
            crypt_arg,
            crypt_arg_is_key: bool,
            create=False
    ):
        """
        Find or create a CryptFileWrap instance
        :param path: pathlib.Path on filesystem for actual encrypted file
        :param crypt_arg: Either a cryptographic key, or the seed for one
        :param crypt_arg_is_key: Whether the crypt_arg is a key (o/w a seed)
        :param create: Whether caller intends to create a new instance
        """
        self.path = path
        self._timestamp = None
        self._ciphertext = None
        if not self.path.exists():
            if create:
                self.salt = make_salt_string()
            else:
                raise FileNotFoundError(
                    f"Matching item not found"
                    f"Did you mean to pass create=True?"
                )
        else:
            if not create:
                with path.open('r') as cf:
                    # the salt was stored as a hexadecimal string
                    self.salt = cf.readline().strip('\n')
                    # the next line is an encrypted datetime stamp
                    self._timestamp = cf.readline().strip('\n')
                    # the next line is the encrypted content
                    self._ciphertext = cf.readline().strip('\n')
            else:
                raise FileExistsError(
                    f"Matching item already exists"
                    f"Did you mean to pass create=False?"
                )
        # couldn't set the encryption key until the salt was set
        if crypt_arg_is_key:
            self.key = crypt_arg
        else:
            self.key = make_crypt_key(crypt_arg, self.salt)
        return

    def delete(self):
        if not self.path.exists():
            raise FileNotFoundError(f"{self.path} does not exist")
        self.path.unlink()

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
