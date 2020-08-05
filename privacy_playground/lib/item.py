"""
Implementation of Item

Item is a base class for things to be stored in a Locker.
"""

# Built-in library packages
from __future__ import annotations
from pathlib import Path
from typing import Union

# Third party packages

# In-project modules
from . crypt_file_wrap import CryptFileWrap


FILE_EXT = "cry"
ITEM_TYPES = ['secret', 'template', 'schema', 'tag']


class Item(object):
    """
    Storage content of a Locker
    """

    item_types = list(ITEM_TYPES)

    def __init__(
            self, locker,
            name: str,
            item_type: str,
            create: bool = False
    ):
        self.locker = locker
        self.item_type = item_type
        self.name = name
        pth = Item.encode_file_name(locker, item_type, name)
        if pth.exists() and create:
            raise FileExistsError(
                f"Matching item found {pth} - "
                f"Did you mean to pass create=False?"
            )
        if not pth.exists() and not create:
            raise FileNotFoundError(
                f"Matching item not found - "
                f"Did you mean to pass create=True?"
            )
        self.crypt = CryptFileWrap(
            Item.encode_file_name(locker, item_type, name),
            locker.crypt_key,
            crypt_arg_is_key=True,
            create=create
        )
        self.crypt.key = locker.crypt_key
        return

    def save(self, overwrite=False):
        self.crypt.write(overwrite=overwrite)
        return

    def __str__(self):
        ret_val = "Item\n"
        ret_val += f"type: {self.item_type}\n"
        ret_val += f"name: {self.name}\n"
        ret_val += f"timestamp: {self.timestamp}\n"
        ret_val += f"content follows (between lines)\n"
        ret_val += f"----------\n"
        ret_val += f"{self.content}"
        ret_val += f"----------"
        return ret_val

    @classmethod
    def delete(cls, locker, name, item_type):
        inst = Item.find(locker, name, item_type)
        inst.crypt.delete()

    @classmethod
    def find(cls, locker, name, item_type) -> Union[Item, None]:
        """
        Find one item - name and type are a natural combination key
        :param locker:
        :param name:
        :param item_type:
        :return:
        """
        try:
            inst = Item(locker, name, item_type, create=False)
        except FileNotFoundError:
            return None
        return inst

    @classmethod
    def find_all(cls, locker, item_type_filter=None, filter_include=True):
        """
        Find matching items in a locker
        Default invocation returns all items.
        :param locker: locker to search for items
        :param item_type_filter: list of item types to include/exclude
        :param filter_include: whether item_type_filter is `include` or exclude
        :return: list of matching items
        """
        if not item_type_filter and not filter_include:
            raise ValueError(f"You are asking to exclude all item types!")
        full_set = set(Item.item_types)
        if not item_type_filter:
            item_type_filter = full_set
        else:
            if type(item_type_filter) is set:
                pass
            if type(item_type_filter) is list:
                item_type_filter = set(item_type_filter)
            elif type(item_type_filter) is str:
                item_type_filter = {item_type_filter}
            else:
                raise TypeError(f"unexpected arg type {type(item_type_filter)}")
        if not item_type_filter <= full_set:
            unknown_types = item_type_filter - full_set
            raise ValueError(
                f"{unknown_types} not found in {Item.item_types}")
        if not filter_include:
            item_type_filter = full_set - item_type_filter
        items = []
        item_gen = locker.path.glob(f"*.{FILE_EXT}")
        for item_path in [it for it in item_gen]:
            inst_type, inst_name = Item.decode_file_name(locker, item_path.name)
            if inst_type:
                if inst_type in item_type_filter:
                    found = Item.find(locker, inst_name, inst_type)
                    items.append(found)
        return items

    @classmethod
    def encode_file_name(cls, locker, item_type, item_name) -> Path:
        """
        Encode and encrypt the item type and name into the
        encrypted file name used to store Items.
        :param locker:
        :param item_type:
        :param item_name:
        :return:
        """
        type_enc = locker.encrypt(item_type)
        name_enc = locker.encrypt(item_name)
        encrypted_name = locker.encrypt(f"{type_enc}:{name_enc}")
        return locker.path.joinpath(f"{encrypted_name}.{FILE_EXT}")

    @classmethod
    def decode_file_name(cls, locker, file_name: str):
        """
        Convert from encrypted, encoded filename format on disk
        and return the item type and name used to create the filename.
        :param locker:
        :param file_name:
        :return:
        """
        # Tolerate with or without file extension
        if file_name.endswith(f".{FILE_EXT}"):
            file_name = file_name[0:-4]
        type_enc, name_enc = locker.decrypt(file_name).decode().split(':')
        item_type = locker.decrypt(type_enc).decode()
        item_name = locker.decrypt(name_enc).decode()
        return item_type, item_name

    @classmethod
    def get_item_types(cls):
        return cls.item_types

    @property
    def content(self):
        """
        Method to get plain text content
        Cipher text is decrypted when this method is invoked.
        :return: Plain text content
        """
        return self.crypt.plaintext

    @content.setter
    def content(self, new_content):
        """
        Method to pass plain text that will be encrypted on the crypt object
        :param new_content: Plain text
        :return:
        """
        self.crypt.plaintext = new_content
        return

    @property
    def timestamp(self):
        return self.crypt.timestamp

    @property
    def salt(self):
        """
        Convenience accessor to crypt.salt
        :return:
        """
        return self.crypt.salt

    @property
    def crypt_key(self):
        """
        Method to get crypt key
        Lack of setter is intentional
        :return: crypt_key
        """
        return self.crypt.key
