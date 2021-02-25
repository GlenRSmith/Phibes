"""
A Locker is a storage unit for user secrets (passwords, etc.)
A Locker is represented by a file "<locker_id>.lck" on the local file system.
A Locker has other data on the file system, but that file
(which contains the single access credentials) is the requisite bit.
"""

# Built-in library packages
from __future__ import annotations
from pathlib import Path
from typing import List

# Third party packages
# In-project modules
from phibes.crypto import get_crypt
from phibes.lib.config import ConfigModel
from phibes.lib.errors import PhibesNotFoundError
from phibes.lib.errors import PhibesUnknownError
from phibes.lib.utils import encode_name, decode_name
from phibes.model import FILE_EXT, Item
from phibes.storage.file_storage import LockerFileStorage


ItemList = List[Item]
# HEX_REGEX = "^(0[xX])?[A-Fa-f0-9]+$"
# HexStr = Match[HEX_REGEX]
# str(type(self)).split("'")[1].split(".")[-1].lower()

LOCKER_FILE = "locker.config"


class Locker(object):
    """
    Locker model object
    """

    _store_impl = LockerFileStorage

    def __init__(self):
        """
        This should only be called by the class methods `get` and `create`
        """
        self.path = None
        self.lock_file = None
        self.crypt_impl = None
        self.timestamp = None

    @staticmethod
    def get_stored_name(name: str) -> str:
        """
        Return the stored locker_id for the user-provided name
        :param name: User-provided locker name
        :return: Name encoded for use in storage (e.g. file system dir)
        """
        return encode_name(name)

    @staticmethod
    def get_name(stored_name: str) -> str:
        """
        Return the user-provided name for the stored locker_id
        :param stored_name: locker_id of locker on storage
        :return: user-provided locker name
        """
        return decode_name(stored_name)

    @classmethod
    def get(cls, password: str, name: str = None) -> Locker:
        """
        Get a Locker object
        @param password: Password for existing locker
        @param name: The optional name of the locker
        @return: Locker instance
        """
        if name is not None:
            name = Locker.get_stored_name(name)
        inst = Locker()
        rec = cls._store_impl.get(locker_id=name)
        pw_hash = rec['body']
        salt = rec['salt']
        crypt_id = rec['crypt_id']
        inst.crypt_impl = get_crypt(crypt_id, password, pw_hash, salt)
        inst.timestamp = rec['timestamp']
        # for the time being, retaining the assignment of
        # filesystem properties to avoid breaking a bunch of tests
        inst.path = rec['path']
        inst.lock_file = rec['lock_file']
        return inst

    @classmethod
    def create(
            cls, password: str, crypt_id: str, name: str = None
    ) -> Locker:
        """
        Create a Locker object
        :param password: Password for the new locker
        :param crypt_id: ID of the crypt_impl to create
        :param name: The optional name of the locker.
                     Must be unique in storage
        """
        if name is not None:
            stored_name = Locker.get_stored_name(name)
        else:
            stored_name = None
        cls._store_impl.create(
            password=password, crypt_id=crypt_id, locker_id=stored_name
        )
        # Verify it is accessible
        try:
            instance = cls.get(password=password, name=name)
        except Exception as err:
            raise PhibesUnknownError(f' unknown {err=}')
        return instance

    @classmethod
    def delete(cls, password: str, name: str = None):
        """Delete a locker"""
        try:
            inst = Locker.get(password=password, name=name)
        except (FileNotFoundError, PhibesNotFoundError):
            # TODO: replace with something like "storage info"
            err_path = ConfigModel().store_path
            err_name = (f" with {name=}!", "!")[name is None]
            err = f"No locker found to delete at {err_path}{err_name}\n"
            raise PhibesNotFoundError(err)
        inst.delete_instance(name=name)

    def delete_instance(self, name: str = None):
        """Instance method to delete locker"""
        items = self.list_items()
        for it in items:
            self.delete_item(it.name)
        self._store_impl.delete(locker_id=self.path.name)

    def decrypt(self, ciphertext: str) -> str:
        """
        Convenience method to decrypt using a Locker object
        :param ciphertext:
        :return:
        """
        return self.crypt_impl.decrypt(ciphertext)

    def encrypt(self, plaintext: str) -> str:
        """
        Convenience method to encrypt using a Locker object
        :param plaintext:
        :return:
        """
        return self.crypt_impl.encrypt(plaintext)

    def get_item_path(self, item_name: str) -> Path:
        file_name = f"{self.encrypt(item_name)}.{FILE_EXT}"
        return self.path.joinpath(file_name)

    def create_item(self, item_name: str) -> Item:
        """
        Creates an in-memory item, prepopulates `content` from named template
        (if provided)
        Client must follow up with `add_item` call to save the new item.
        @param item_name: locker_id of new item
        @return: new in-memory item
        """
        return Item(self.crypt_impl, item_name)

    def save_item(self, item: Item, replace: bool) -> None:
        """
        Saves the new item to the locker
        @param item: item to save
        @param replace: whether this is replacing a stored item
        @return: None
        """
        item_rec = item.as_dict()
        item_id = self.encrypt(item.name)
        locker_id = self.path.name
        return self._store_impl.save_item(
            item_id=item_id,
            item_rec=item_rec,
            locker_id=locker_id,
            replace=replace
        )

    def add_item(self, item: Item) -> None:
        """
        Saves the new item to the locker
        @param item: item to save
        @return: None
        """
        return self.save_item(item=item, replace=False)

    def get_item(self, item_name: str) -> Item:
        """
        Attempts to find and return a named item in the locker.
        Raises an exception of item isn't found
        @param item_name: locker_id of item (plaintext)
        @return: the item
        """
        rec = Locker._store_impl.get_item(
            item_id=self.encrypt(item_name),
            locker_id=self.path.name  # already hashed locker name
        )
        item = Item.make_item_from_dict(
            crypt_obj=self.crypt_impl, name=item_name, item_dict=rec
        )
        if not item:
            raise PhibesNotFoundError(f"{item_name} not found")
        elif not self.crypt_impl.salt == item.salt:
            raise PhibesUnknownError(
                f"found item {item_name} but salt mismatch"
                f" which really seems impossible but here we are"
            )
        return item

    def update_item(self, item: Item) -> None:
        """
        Save `item`, allowing overwrite
        :param item: Item instance to save
        """
        return self.save_item(item=item, replace=True)

    def delete_item(self, item_name: str) -> None:
        """
        Delete item from locker
        :param item_name: name of item to delete
        """
        try:
            return self._store_impl.delete_item(
                item_id=self.encrypt(item_name),
                locker_id=self.path.name
            )
        except FileNotFoundError as err:
            raise PhibesNotFoundError(
                f"Item not found {item_name}"
                f"extra info {err}"
            )

    def list_items(self) -> ItemList:
        """
        Return a list of Items of the specified type in this locker
        :return:
        """
        items = []
        item_ids = Locker._store_impl.list_items(locker_id=self.path.name)
        for item_id in item_ids:
            item = self.get_item(item_name=self.decrypt(item_id))
            items.append(item)
        return items
