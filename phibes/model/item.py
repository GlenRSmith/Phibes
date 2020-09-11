"""
Implementation of Item

Item is a base class for things to be stored in a Locker.
"""

# Built-in library packages
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Optional

# Third party packages

# In-project modules
from phibes.lib.crypto import CryptImpl
from phibes.lib import phibes_file


FILE_EXT = "cry"


class Item(object):
    """
    Storage content of a Locker
    """

    def __init__(
            self,
            crypt_obj: CryptImpl,
            name: str,
            content: Optional[str] = None
    ):
        self.item_type = self.get_type_name()
        self.name = name
        self.crypt_impl = crypt_obj
        self._ciphertext = None
        self._timestamp = None
        if content:
            self.content = content
        return

    def save(self, pth: Path, overwrite: bool = False):
        self._timestamp = self.crypt_impl.encrypt(
            str(datetime.now())
        )
        phibes_file.write(
            pth,
            self.salt,
            self.crypt_impl.guid,
            self._timestamp,
            self._ciphertext,
            overwrite=overwrite
        )
        return

    def read(self, pth: Path) -> None:
        """
        Read an Item from the file at pth
        Caller (a locker) is responsible for any validation.
        e.g. does the salt in the file and the locker key
        produce the encoded/encrypted file name?
        If not, the contents won't be decrypted correctly.
        :param pth:
        :return:
        """
        rec = phibes_file.read(pth)
        self._salt = rec['salt']
        self._timestamp = rec['timestamp']
        self._ciphertext = rec['body']
        # crypt_impl will have generated a random salt,
        # need to set it to the correct one for this item
        self.crypt_impl.salt = self._salt

    def __str__(self):
        ret_val = "Item\n"
        ret_val += f"type: {self.item_type}\n"
        ret_val += f"name: {self.name}\n"
        ret_val += f"timestamp: {self.timestamp}\n"
        ret_val += f"content follows (between lines)\n"
        ret_val += f"----------\n"
        ret_val += f"{self.content}"
        ret_val += f"\n----------\n"
        return ret_val

    @classmethod
    def get_type_name(cls):
        return str(cls).split("'")[1].split(".")[-1].lower()

    @property
    def content(self):
        """
        Method to get plain text content
        Cipher text is decrypted when this method is invoked.
        :return: Plain text content
        """
        return self.crypt_impl.decrypt(self._ciphertext)

    @content.setter
    def content(self, content):
        """
        Method to pass plain text that will be encrypted on the crypt object
        :param content: Plain text
        :return:
        """
        self._ciphertext = self.crypt_impl.encrypt(content)
        return

    @property
    def timestamp(self):
        try:
            ret_val = self.crypt_impl.decrypt(self._timestamp)
        except Exception:
            ret_val = datetime.now()
        return str(ret_val)

    @property
    def ciphertext(self):
        return self._ciphertext

    @property
    def salt(self):
        """
        Convenience accessor to crypt.salt
        :return:
        """
        return self.crypt_impl.salt

    @property
    def crypt_key(self):
        """
        Method to get crypt key
        Lack of setter is intentional
        :return: crypt_key
        """
        return self.crypt_impl.key