"""
A Locker is a storage unit for user secrets (passwords, etc.)
A Locker is represented by a file "<name>.lck" on the local file system.
A Locker has other data on the file system, but that file
(which contains the single access credentials) is the requisite bit.
"""

# Built-in library packages
from __future__ import annotations
import base64
from datetime import datetime
from pathlib import Path
import shutil
from typing import List

# Third party packages

# In-project modules
from phibes.crypto import create_crypt, get_crypt
from phibes.lib import phibes_file
from phibes.lib.config import ConfigModel
from phibes.lib.errors import PhibesExistsError
from phibes.lib.errors import PhibesNotFoundError
from phibes.lib.errors import PhibesUnknownError
from phibes.model import FILE_EXT, Item


ItemList = List[Item]
# HEX_REGEX = "^(0[xX])?[A-Fa-f0-9]+$"
# HexStr = Match[HEX_REGEX]
# str(type(self)).split("'")[1].split(".")[-1].lower()

LOCKER_FILE = "locker.config"


class Locker(object):
    """
    Locker model object
    """

    def __init__(self):
        """
        This should only be called by the class methods `get` and `create`
        """
        self.path = None
        self.lock_file = None
        self.crypt_impl = None
        self.timestamp = None

    @staticmethod
    def get_pw_hash(storage_path: Path) -> str:
        """
        Method to get the stored password hash without authenticating
        :param storage_path: Filesystem path to the locker
        :return: pw_hash
        """
        msgs = f"{storage_path}\n"
        lock_file = storage_path / LOCKER_FILE
        if not lock_file.exists():
            raise PhibesNotFoundError(msgs)
        else:
            msgs += f"... {lock_file.resolve()}\n"
            rec = phibes_file.read(lock_file)
            pw_hash = rec['body']
        return pw_hash

    @staticmethod
    def get_stored_name(name: str) -> str:
        """
        Return the stored name for the user-provided name
        :param name: User-provided locker name
        :return: Name encoded for use in storage (e.g. file system dir)
        """
        return base64.urlsafe_b64encode(name.encode()).rstrip(b"=").decode()

    @staticmethod
    def get_name(stored_name: str) -> str:
        """
        Return the user-provided name for the stored name
        :param stored_name: name of locker on storage
        :return: user-provided locker name
        """
        padding = 4 - (len(stored_name.encode()) % 4)
        return base64.urlsafe_b64decode(
            stored_name.encode() + (b"=" * padding)
        ).decode()

    @classmethod
    def get(cls, password: str, name: str = None, path: str = None) -> Locker:
        """
        Get a Locker object
        @param password: Password for existing locker
        @param name: The optional name of the locker
        @param path: The optional path to the locker
        @return: Locker instance
        """
        if path is None:
            storage_path = Path(ConfigModel().store_path)
        else:
            storage_path = path
        if name:
            storage_path = storage_path / Locker.get_stored_name(name)
        msgs = f"{storage_path=}\n"
        inst = Locker()
        inst.lock_file = storage_path / LOCKER_FILE
        if not inst.lock_file.exists():
            raise PhibesNotFoundError(msgs)
        else:
            inst.path = storage_path
            msgs += f"... {inst.lock_file.resolve()}\n"
            rec = phibes_file.read(inst.lock_file)
            pw_hash = rec['body']
            salt = rec['salt']
            crypt_id = rec['crypt_id']
            msgs += f"trying {crypt_id=} {password=} {pw_hash=}\n"
            inst.crypt_impl = get_crypt(crypt_id, password, pw_hash, salt)
            inst.timestamp = rec['timestamp']
        return inst

    @classmethod
    def create(
            cls, password: str,
            crypt_id: str,
            name: str = None,
            path: str = None
    ):
        """
        Create a Locker object
        :param password: Password for the new locker
        :param crypt_id: ID of the crypt_impl to create
        :param name: The optional name of the locker. Must be unique in storage
        :param path: The optional path to the locker.
        """
        if path is None:
            storage_path = Path(ConfigModel().store_path)
        else:
            storage_path = path
        if name:
            storage_path = storage_path / Locker.get_stored_name(name)
            try:
                storage_path.mkdir(exist_ok=False)
            except FileExistsError as err:
                raise PhibesExistsError(err)
        if not Locker.can_create(storage_path, remove_if_empty=False):
            raise ValueError(f"could not create {storage_path}")
        try:
            Locker.get(password=password, name=name, path=storage_path)
        except PhibesNotFoundError:
            pass
        inst = Locker()
        inst.crypt_impl = create_crypt(password, crypt_id)
        inst.path = storage_path
        inst.lock_file = inst.path / LOCKER_FILE
        phibes_file.write(
            inst.lock_file,
            inst.crypt_impl.salt,
            inst.crypt_impl.crypt_id,
            str(datetime.now()),
            inst.crypt_impl.pw_hash,
            overwrite=False
        )
        return inst

    @classmethod
    def delete(cls, password: str, name: str = None, path: str = None):
        """Delete a locker"""
        try:
            inst = Locker.get(password=password, name=name, path=path)
        except (FileNotFoundError, PhibesNotFoundError):
            err_path = (path, ConfigModel().store_path)[path is None]
            err_name = (f" with {name=}!", f"!")[name is None]
            err = f"No locker found to delete at {err_path}{err_name}\n"
            raise PhibesNotFoundError(err)
        inst.delete_instance(name=name)

    def delete_instance(self, name: str = None):
        """Instance method to delete locker"""
        items = self.list_items()
        for it in items:
            self.delete_item(it.name)
        Path(self.lock_file).unlink()
        # only remove a directory when it was created for this locker
        if name:
            shutil.rmtree(self.path)

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
                raise PhibesExistsError(
                    f"{locker_path} already exists and is not a directory"
                )
            if bool(list(locker_path.glob('*'))):
                raise PhibesExistsError(
                    f"dir {locker_path} already exists and is not empty"
                )
            else:
                if remove_if_empty:
                    locker_path.rmdir()
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
        @param item_name: name of new item
        @return: new in-memory item
        """
        return Item(self.crypt_impl, item_name)

    def add_item(self, item: Item) -> None:
        """
        Saves the item to the locker
        @param item: item to save
        @return: None
        """
        pth = self.get_item_path(item.name)
        item.save(pth, overwrite=False)
        return

    def get_item(self, item_name: str) -> Item:
        """
        Attempts to find and return a named item in the locker.
        Raises an exception of item isn't found
        @param item_name: name of item
        @return: the item
        """
        pth = self.get_item_path(item_name)
        if pth.exists():
            found_item = Item(self.crypt_impl, item_name)
            found_item.read(pth)
            if not self.crypt_impl.salt == found_item.salt:
                raise PhibesUnknownError(
                    f"found item {item_name} but salt mismatch"
                    f" which really seems impossible but here we are"
                )
        else:
            raise PhibesNotFoundError(f"{item_name} not found")
        return found_item

    def update_item(self, item: Item) -> None:
        """
        Save `item`, allowing overwrite
        :param item: Item instance to save
        """
        pth = self.get_item_path(item.name)
        item.save(pth, overwrite=True)
        return

    def delete_item(self, item_name: str) -> None:
        """
        Delete item from locker
        :param item_name: name of item to delete
        """
        self.get_item_path(item_name).unlink()

    def list_items(self) -> ItemList:
        """
        Return a list of Items of the specified type in this locker
        :return:
        """
        items = []
        item_gen = self.path.glob(f"*.{FILE_EXT}")
        ext_len = len(FILE_EXT) + 1
        for item_path in [it for it in item_gen]:
            inst_name = self.decrypt(item_path.name[0:-ext_len])
            found = self.get_item(inst_name)
            items.append(found)
        return items
