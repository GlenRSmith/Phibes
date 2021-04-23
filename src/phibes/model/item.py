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
from phibes.crypto.crypt_ifc import CryptIfc
from phibes.lib import phibes_file


FILE_EXT = "cry"


class Item(object):
    """
    Storage content of a Locker
    """

    def __init__(
            self,
            crypt_obj: CryptIfc,
            name: str,
            content: Optional[str] = None
    ):
        self.name = name
        self.crypt_impl = crypt_obj
        self._ciphertext = None
        self.timestamp = str(datetime.now())
        if content:
            self.content = content
        return

    def save(self, pth: Path, overwrite: bool = False):
        phibes_file.write(
            pth=pth,
            salt=self.salt,
            crypt_id=self.crypt_impl.crypt_id,
            timestamp=self.timestamp,
            body=self._ciphertext,
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
        Item.make_item_from_dict(
            crypt_obj=self.crypt_impl,
            name=self.name,
            item_dict=rec,
            item_inst=self
        )

    @classmethod
    def make_item_from_dict(
            cls, crypt_obj: CryptIfc,
            name: str,
            item_dict: dict,
            item_inst: Item = None
    ) -> Item:
        if item_inst is None:
            item_inst = Item(crypt_obj=crypt_obj, name=name)
        item_inst._salt = item_dict['salt']
        item_inst.timestamp = item_dict['timestamp']
        item_inst._ciphertext = item_dict['body']
        # crypt_impl will have generated a random salt,
        # need to set it to the correct one for this item
        item_inst.crypt_impl.salt = item_inst._salt
        return item_inst

    def as_dict(self):
        ret_val = {
            'salt': self.salt,
            'crypt_id': self.crypt_impl.crypt_id,
            'timestamp': self.timestamp,
            'body': self.content,
            'name': self.name,
            '_ciphertext': self._ciphertext
        }
        return ret_val

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
