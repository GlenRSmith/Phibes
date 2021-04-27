"""
A Locker is a storage unit for user secrets (passwords, etc.)
A Locker is represented by a file "<locker_id>.lck" on the local file system.
A Locker has other data on the file system, but that file
(which contains the single access credentials) is the requisite bit.
"""

# Built-in library packages
from __future__ import annotations
from json import dumps
from typing import List

# Third party packages
# In-project modules
from phibes.crypto import create_crypt, get_crypt
from phibes.crypto.crypt_ifc import CryptIfc
from phibes.lib.config import ConfigModel
from phibes.lib.errors import PhibesNotFoundError, PhibesUnknownError
from phibes.lib.utils import encode_name
from phibes.model import Item
from phibes.model.model import LockerModel


LOCKER_FILE = "locker.config"


class Locker(object):
    """
    Locker model object
    """

    def __init__(
            self, crypt_impl: CryptIfc, locker_name: str = None, **kwargs
    ):
        """
        This should only be called by the class methods `get` and `create`
        """
        self.crypt_impl = crypt_impl
        self.locker_name = locker_name
        self.timestamp = kwargs.get('timestamp')
        self._model = None

    @property
    def data_model(self):
        if self._model is None:
            self._model = LockerModel(locker_id=self.locker_id)
        return self._model

    @property
    def locker_id(self):
        if self.locker_name is None:
            return None
        return Locker.get_locker_id(self.locker_name)

    @classmethod
    def get_locker_id(cls, locker_name):
        if locker_name is None:
            return None
        return encode_name(locker_name)

    @classmethod
    def get(cls, password: str, locker_name: str = None) -> Locker:
        """
        Get a Locker object
        @param password: Password for existing locker
        @param locker_name: The optional name of the locker
        @return: Locker instance
        """
        lid = Locker.get_locker_id(locker_name=locker_name)
        locker = LockerModel(locker_id=lid)
        crypt_inst = get_crypt(password=password, **locker.__dict__)
        inst = Locker(
            crypt_impl=crypt_inst, locker_name=locker_name, **locker.__dict__
        )
        return inst

    @classmethod
    def create(
            cls, password: str, crypt_id: str, locker_name: str = None
    ) -> Locker:
        """
        Create a Locker object
        :param password: Password for the new locker
        :param crypt_id: ID of the crypt_impl to create
        :param locker_name: The optional name of the locker.
                     Must be unique in storage
        """
        crypt_inst = create_crypt(password=password, crypt_id=crypt_id)
        LockerModel(
            pw_hash=crypt_inst.pw_hash,
            salt=crypt_inst.salt,
            locker_id=Locker.get_locker_id(locker_name=locker_name),
            crypt_id=crypt_inst.crypt_id
        )
        # Verify it is accessible
        try:
            instance = cls.get(password=password, locker_name=locker_name)
        except Exception as err:
            raise PhibesUnknownError(f' unknown {err=}')
        if not instance:
            raise PhibesNotFoundError(locker_name)
        return instance

    @classmethod
    def delete(cls, password: str, locker_name: str = None):
        """Delete a locker"""
        try:
            inst = Locker.get(
                password=password, locker_name=locker_name
            )
        except (FileNotFoundError, PhibesNotFoundError):
            err_path = ConfigModel().store
            err_name = (f" with {locker_name=}!", "!")[locker_name is None]
            err = f"No locker found to delete at {err_path}{err_name}\n"
            raise PhibesNotFoundError(err)
        return inst.data_model.delete()

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

    def create_item(self, item_name: str) -> Item:
        """
        Creates an in-memory item
        Client must follow up with `add_item` call to save the new item.
        @param item_name: name of new item
        @return: new in-memory item
        """
        return Item(self.crypt_impl, item_name)

    def save_item(self, item: Item, replace: bool) -> Item:
        """
        Saves the new item to the locker
        @param item: item to save
        @param replace: whether this is replacing a stored item
        @return: None
        """
        if replace:
            self.data_model.update_item(
                item_id=self.crypt_impl.encrypt(item.name),
                content=self.crypt_impl.encrypt(item.content),
                timestamp=item.timestamp
            )
        else:
            self.data_model.create_item(
                item_id=self.crypt_impl.encrypt(item.name),
                content=self.crypt_impl.encrypt(item.content),
                timestamp=item.timestamp
            )
        return item

    def add_item(self, item: Item) -> Item:
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
        rec = self.data_model.get_item(
            item_id=self.crypt_impl.encrypt(item_name)
        )
        item = Item.make_item_from_dict(
            crypt_obj=self.crypt_impl,
            name=item_name,
            item_dict=rec
        )
        if not item:
            raise PhibesNotFoundError(f"{item_name} not found")
        elif not self.crypt_impl.salt == item.salt:
            raise PhibesUnknownError(
                f"found item {item_name} but salt mismatch"
                f" which really seems impossible but here we are"
            )
        return item

    def update_item(self, item: Item) -> Item:
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
            return self.data_model.delete_item(
                item_id=self.crypt_impl.encrypt(item_name)
            )
        except FileNotFoundError as err:
            raise PhibesNotFoundError(
                f"Item not found {item_name}"
                f"extra info {err}"
            )

    def list_items(self) -> List[Item]:
        """
        Return a list of Items of the specified type in this locker
        :return:
        """
        items = []
        item_ids = self.data_model.get_items()
        for item_id in item_ids:
            item = self.get_item(item_name=self.decrypt(item_id))
            items.append(item)
        return items

    def to_dict(self, **kwargs):
        """
        Provide design dict representation of locker
        self.locker_name = locker_name
        """
        ret_dict = {
            'timestamp': self.timestamp,
            'crypt_id': self.crypt_impl.crypt_id,
            'storage': dumps(
                self.data_model.storage.__dict__, default=str
            )
        }
        if hasattr(self, 'locker_name') and self.locker_name:
            ret_dict['locker_name'] = self.locker_name
        return ret_dict
