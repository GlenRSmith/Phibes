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
# from phibes.lib.errors import PhibesAuthError, PhibesConfigurationError
from phibes.lib.errors import PhibesNotFoundError, PhibesExistsError
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
        Opening an interface to an existing locker
        :param name: The name of the locker
        :param password: Password for the locker
        """
        conf = ConfigModel()
        inst = Locker()
        path = conf.store_path
        # start a string for verbose error/debugging
        msgs = f"{path=}\n{name=}\n"
        full_path = conf.store_path / Locker.get_stored_name(name)
        lockfile = full_path / LOCKER_FILE
        if not lockfile.exists():
            raise PhibesNotFoundError(msgs)
        else:
            inst.path = full_path
            inst.lock_file = lockfile
            msgs += f"... {lockfile.resolve()}\n"
            rec = phibes_file.read(lockfile)
            pw_hash = rec['body']
            salt = rec['salt']
            crypt_id = rec['crypt_id']
            msgs += f"trying {crypt_id=} {password=} {pw_hash=}\n"
            inst.crypt_impl = get_crypt(crypt_id, password, pw_hash, salt)
        return inst

    @classmethod
    def create(cls, name: str, password: str, crypt_id: str = None):
        """
        Create a Locker object
        :param name: The name of the locker. Must be unique in storage
        :param password: Password for the new locker
        :param crypt_id: ID of the crypt_impl to create
        """
        try:
            Locker.get(name, password)
        except PhibesNotFoundError:
            pass
        inst = Locker()
        inst.crypt_impl = create_crypt(password, crypt_id)
        inst.path = Path(
            ConfigModel().store_path.joinpath(
                Locker.get_stored_name(name)
            )
        )
        inst.lock_file = inst.path / LOCKER_FILE
        if not Locker.can_create(inst.path):
            raise ValueError(f"could not create {name}")
        inst.path.mkdir(exist_ok=False)
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
        Attempts to find and return an item in the locker
        with the given name and type.
        Raises an exception of item isn't found
        @param item_name: name of item
        @return: the item
        """
        pth = self.get_item_path(item_name)
        if pth.exists():
            found_item = Item(self.crypt_impl, item_name)
            found_item.read(pth)
            # TODO: validate using salt
        else:
            raise PhibesNotFoundError(f"{item_name} not found")
        return found_item

    def update_item(self, item: Item) -> None:
        pth = self.get_item_path(item.name)
        item.save(pth, overwrite=True)
        return

    def delete_item(self, item_name: str) -> None:
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
