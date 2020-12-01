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
from typing import List, Optional

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

LOCKER_FILE = ".config"


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
        return

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
    def get(cls, name: str, password: str):
        """
        Opening an interface to a named, existing locker
        :param name: The name of the locker
        :param password: Password for the locker
        """
        conf = ConfigModel()
        full_path = conf.store_path / Locker.get_stored_name(name)
        return Locker.get_anonymous(full_path, password)

    @classmethod
    def get_anonymous(cls, storage_path: Path, password: str):
        """
        Opening an interface to an existing locker
        :param storage_path: The filesystem path to the locker
        :param password: Password for the locker
        """
        inst = Locker()
        # start a string for verbose error/debugging
        msgs = f"{storage_path=}\n"
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
        return inst

    @classmethod
    def create(cls, name: str, password: str, crypt_id: str = None):
        """
        Create a named Locker object
        :param name: The name of the locker. Must be unique in storage
        :param password: Password for the new locker
        :param crypt_id: ID of the crypt_impl to create
        """
        try:
            Locker.get(name, password)
        except PhibesNotFoundError:
            pass
        storage_path = Path(
            ConfigModel().store_path.joinpath(Locker.get_stored_name(name))
        )
        if not Locker.can_create(storage_path):
            raise ValueError(f"could not create {name}")
        storage_path.mkdir(exist_ok=False)
        return Locker.create_anonymous(storage_path, password, crypt_id)

    @classmethod
    def create_anonymous(
            cls, storage_path: Path, password: str, crypt_id: str = None
    ):
        """
        Create a Locker object
        :param storage_path: Filesystem path for storage of locker
        :param password: Password for the new locker
        :param crypt_id: ID of the crypt_impl to create
        """
        try:
            Locker.get_anonymous(storage_path, password)
        except PhibesNotFoundError:
            pass
        inst = Locker()
        inst.crypt_impl = create_crypt(password, crypt_id)
        inst.path = storage_path
        inst.lock_file = inst.path / LOCKER_FILE
        if not Locker.can_create(inst.path, remove_if_empty=False):
            raise ValueError(f"could not create {storage_path}")
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
    def delete(cls, name: str, password: str):
        try:
            inst = Locker.get(name, password)
        except FileNotFoundError:
            inst = None
        if inst:
            shutil.rmtree(inst.path)
        else:
            raise PhibesNotFoundError(
                f"Locker {name} not found to delete!\n"
                f"{ConfigModel().store_path}\n"
            )

    @classmethod
    def delete_anonymous(cls, storage_path: Path, password: str):
        try:
            inst = Locker.get_anonymous(storage_path, password)
        except FileNotFoundError:
            inst = None
        if inst:
            shutil.rmtree(storage_path)
        else:
            raise PhibesNotFoundError(
                f"Locker {storage_path} not found to delete!\n"
            )

    @classmethod
    def find(cls, name: str, password: str) -> Optional[Locker]:
        """
        Find and return the matching locker
        :param name: Plaintext name of locker
        :param password: Locker password
        :return: Found Locker or None
        """
        try:
            inst = Locker.get(name, password)
        except FileNotFoundError as err:
            raise PhibesNotFoundError(
                f"Locker {name} not found\n"
                f"{err}"
            )
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

    def create_item(
            self, item_name: str,
            template_name: Optional[str] = None
    ) -> Item:
        """
        Creates an in-memory item, prepopulates `content` from named template
        (if provided)
        Client must follow up with `add_item` call to save the new item.
        @param item_name: name of new item
        @param template_name: name of (optional) template item
        @return: new in-memory item
        """
        new_item = Item(self.crypt_impl, item_name)
        if template_name:
            template = self.get_item(template_name)
            if not template:
                raise PhibesNotFoundError(
                    f"template {template_name} not found"
                )
            new_item.content = template.content
        return new_item

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
        for item_path in [it for it in item_gen]:
            inst_name = self.decrypt(item_path.name[0:-4])
            found = self.get_item(inst_name)
            items.append(found)
        return items
