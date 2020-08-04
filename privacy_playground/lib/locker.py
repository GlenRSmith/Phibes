"""
A Locker is a storage unit for user secrets (passwords, etc.)
A Locker is represented by a file "<name>.lck" on the local file system.
A Locker has other data on the file system, but that file
(which contains the single access credentials) is the requisite bit.
"""

# Built-in library packages
from __future__ import annotations
from pathlib import Path
import shutil
from typing import List, Union

# Third party packages

# In-project modules
from . config import Config
from . crypto import authenticate_password
from . crypto import get_name_hash, get_password_hash
from . crypto import encrypt, decrypt
from . crypt_file_wrap import CryptFileWrap
from . item import FILE_EXT, Item


ItemList = List[Item]


class Locker(object):

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

    def __init__(self, name: str, password: str, create: bool = False):
        """
        A Locker object can be constructed in two scenarios:
        - client code is creating a new, empty locker
          - this method should create the locker on disk
        - client code is opening an interface to an existing locker
          - this method should try to open the locker on disk
        :param name: The name of the locker. Must be unique in storage
        """
        self.conf = Config('.')
        # TODO: should this be abstracted to "confirm installed" or something?
        self.conf.assure_users_dir()
        if self.conf.hash_locker_names:
            self.path = self.conf.users_path.joinpath(get_name_hash(name))
        else:
            self.path = self.conf.users_path.joinpath(name)
        self.lock_file = self.path.joinpath(".locker.cfg")
        if self.lock_file.exists():
            if not create:
                self.crypt = CryptFileWrap(
                    self.lock_file,
                    password,
                    crypt_arg_is_key=False,
                    create=create
                )
                authenticate_password(
                    password, self.crypt.ciphertext, self.crypt.salt
                )
            else:
                raise FileExistsError(
                    f"Matching locker already exists"
                    f"Did you mean to pass create=False?"
                )
        else:
            if create:
                if not Locker.can_create(self.path):
                    raise ValueError(f"could not create {name}")
                self.path.mkdir(exist_ok=False)
                self.crypt = CryptFileWrap(
                    self.lock_file,
                    password,
                    crypt_arg_is_key=False,
                    create=create
                )
                self.crypt.plaintext = get_password_hash(
                    password, self.crypt.salt
                ).hex()
                self.crypt.write()
            else:
                raise FileNotFoundError(
                    f"Matching locker not found"
                    f"Did you mean to pass create=True?"
                )
        return

    @classmethod
    def delete(cls, name: str, password: str):
        inst = Locker(name, password)
        if inst:
            shutil.rmtree(inst.path)

    @classmethod
    def find(cls, name: str, password: str) -> Union[Locker, None]:
        """
        Find and return the matching locker
        :param name: Plaintext name of locker
        :param password: Locker password
        :return: Found Locker or None
        """
        try:
            inst = Locker(name, password, create=False)
        except FileNotFoundError:
            return None
        return inst

    @classmethod
    def can_create(cls, locker_path: Path, remove_if_empty=True) -> bool:
        """
        Evaluates whether the filesystem allows creation of a new locker.
        :param locker_path: Path to a specific user Locker
        :param remove_if_empty: If the path exists but is empty, remove it?
        :return: None
        """
        if locker_path.exists():
            if not locker_path.is_dir():
                raise FileExistsError(
                    f"{locker_path} already exists and is not a directory"
                )
            if bool(list(locker_path.glob('*'))):
                raise FileExistsError(
                    f"dir {locker_path} already exists and is not empty"
                )
            else:
                if remove_if_empty:
                    locker_path.rmdir()
                else:
                    return False
        return True

    def validate(self):
        if not self.path.exists():
            raise ValueError(f"Locker path {self.path} does not exist")
        if not self.path.is_dir():
            raise ValueError(f"Locker path {self.path} not a directory")
        if not self.lock_file.exists():
            raise ValueError(f"Locker file {self.lock_file} does not exist")
        if not self.lock_file.is_file():
            raise ValueError(f"{self.lock_file} is not a file")

    def decrypt(self, ciphertext: str) -> str:
        """
        Convenience method to decrypt using a Locker object
        :param ciphertext:
        :return:
        """
        return decrypt(
            self.crypt_key, bytes.fromhex(self.salt), ciphertext
        )

    def encrypt(self, plaintext: str) -> str:
        """
        Convenience method to encrypt using a Locker object
        :param plaintext:
        :return:
        """
        iv, ciphertext = encrypt(
            self.crypt_key, plaintext, iv=bytes.fromhex(self.salt)
        )
        return ciphertext

    def list_items(self, item_type=None) -> ItemList:
        """
        Return a list of Items of the specified type in this locker
        :param item_type: type of Items (e.g. Secret) to list, None = all
        :return:
        """
        if item_type:
            if type(item_type) is not list:
                item_type = [item_type]
            missing_types = []
            for it in item_type:
                if it not in Item.get_item_types():
                    missing_types.append(it)
            if missing_types:
                raise ValueError(
                    f"{missing_types} not found in {Item.get_item_types()}")
        else:
            item_type = Item.get_item_types()
        items = []
        item_gen = self.path.glob(f"*.{FILE_EXT}")
        for item_path in [it for it in item_gen]:
            inst_type, inst_name = Item.decode_file_name(self, item_path.name)
            if inst_type:
                if inst_type not in Item.get_item_types():
                    raise ValueError(f"{item_type} is not a valid item type")
                else:
                    if inst_type in item_type:
                        found = Item.find(self, inst_name, inst_type)
                        items.append(found)
        return items
