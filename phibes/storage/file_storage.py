"""
A Locker is a storage unit for user secrets (passwords, etc.)
A Locker is represented by a file "<name>.lck" on the local file system.
A Locker has other data on the file system, but that file
(which contains the single access credentials) is the requisite bit.
"""

# Built-in library packages
from __future__ import annotations
# import base64
from datetime import datetime
from pathlib import Path
# import shutil
# from typing import List

# Third party packages

# In-project modules
from phibes.crypto import create_crypt
# from phibes.crypto import get_crypt
from phibes.lib import phibes_file
from phibes.lib.config import ConfigModel
from phibes.lib.errors import PhibesExistsError
from phibes.lib.errors import PhibesNotFoundError
# from phibes.lib.errors import PhibesUnknownError
from phibes.model import FILE_EXT
# from phibes.model import Item
# from phibes.lib.utils import ReprType, todict

# In-package modules
from .storage_impl import StorageImpl


LOCKER_FILE = "locker.config"


def get_locker_path(locker_id: str = None) -> Path:
    """Convenience function for getting path to a locker"""
    storage_path = Path(ConfigModel().store_path)
    if locker_id is None:
        locker_path = storage_path
    else:
        locker_path = storage_path / locker_id
    return locker_path


def get_item_path(item_id: str, locker_id: str = None) -> Path:
    """Convenience function for getting path to an item"""
    locker_path = get_locker_path(locker_id=locker_id)
    return locker_path / f"{item_id}.{FILE_EXT}"


class LockerFileStorage(StorageImpl):

    @classmethod
    def get(cls, locker_id: str = None) -> dict:
        """
        Get a stored Locker from file
        @param locker_id: The optional name of the locker
        @return: LockerFileStorage instance
        """
        locker_path = get_locker_path(locker_id=locker_id)
        lf = locker_path / LOCKER_FILE
        if not lf.exists():
            raise PhibesNotFoundError
        else:
            rec = phibes_file.read(lf)
            rec['lock_file'] = lf
            rec['path'] = locker_path
        return rec

    @classmethod
    def create(
            cls, password: str,
            crypt_id: str,
            name: str = None
    ):
        """
        Create a Locker object
        :param password: Password for the new locker
        :param crypt_id: ID of the crypt_impl to create
        :param name: The optional name of the locker. Must be unique in storage
        """
        storage_path = Path(ConfigModel().store_path)
        if name:
            storage_path = storage_path / name
            try:
                storage_path.mkdir(exist_ok=False)
            except FileExistsError as err:
                raise PhibesExistsError(err)
        if not cls.can_create(storage_path, remove_if_empty=False):
            raise ValueError(f"could not create {storage_path}")
        try:
            cls.get(locker_id=name)
        except PhibesNotFoundError:
            pass
        crypt_impl = create_crypt(password, crypt_id)
        phibes_file.write(
            storage_path / LOCKER_FILE,
            crypt_impl.salt,
            crypt_impl.crypt_id,
            str(datetime.now()),
            crypt_impl.pw_hash,
            overwrite=False
        )
        return cls.get(locker_id=name)

    # @classmethod
    # def delete(cls, password: str, name: str = None):
    #     """Delete a locker"""
    #     storage_path = Path(ConfigModel().store_path)
    #     if name:
    #         storage_path = storage_path / name
    #     try:
    #         inst = Locker.get(password=password, name=name)
    #     except (FileNotFoundError, PhibesNotFoundError):
    #         err_path = (path, ConfigModel().store_path)[path is None]
    #         err_name = (f" with {name=}!", f"!")[name is None]
    #         err = f"No locker found to delete at {err_path}{err_name}\n"
    #         raise PhibesNotFoundError(err)
    #     inst.delete_instance(name=name)
    #
    # def delete_instance(self, name: str = None):
    #     """Instance method to delete locker"""
    #     items = self.list_items()
    #     for it in items:
    #         self.delete_item(it.name)
    #     Path(self.lock_file).unlink()
    #     # only remove a directory when it was created for this locker
    #     if name:
    #         shutil.rmtree(self.path)

    @classmethod
    def get_item(cls, item_id: str, locker_id: str = None) -> dict:
        """
        Attempts to find and return a named item in the locker.
        Raises an exception of item isn't found
        @param item_id: ID of item - encryption of the item_name
        @param locker_id: ID of locker - hash of the locker name
        @return: the item dict
        """
        item_path = get_item_path(
            item_id=item_id, locker_id=locker_id
        )
        if item_path.exists():
            return phibes_file.read(item_path)
        else:
            raise PhibesNotFoundError(f"{item_id} not found")

    @classmethod
    def list_items(cls, locker_id: str = None) -> list:
        """
        Return a list of Items of the specified type in this locker
        :return:
        """
        items = []
        locker_path = get_locker_path(locker_id)
        item_gen = locker_path.glob(f"*.{FILE_EXT}")
        ext_len = len(FILE_EXT) + 1
        for item_path in [it for it in item_gen]:
            stored_name = item_path.name[0:-ext_len]
            items.append(stored_name)
        return items

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

    @classmethod
    def add_item(
            cls, item_id: str, item_rec: dict, locker_id: str = None
    ) -> None:
        """
        Saves the item to the locker
        @param item_id: Encrypted item name
        @param item_rec: contents of item
        @param locker_id: Optional hashed locker name
        @return: None
        """
        item_path = get_item_path(item_id=item_id, locker_id=locker_id)
        phibes_file.write(
            pth=item_path,
            salt=item_rec['salt'],
            crypt_id=item_rec['crypt_id'],
            timestamp=item_rec['timestamp'],
            body=item_rec['_ciphertext'],
        )
