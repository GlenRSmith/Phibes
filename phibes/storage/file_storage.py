"""
A Locker is a storage unit for user secrets (passwords, etc.)
A Locker is represented by a file "<locker_id>.lck" on the local file system.
A Locker has other data on the file system, but that file
(which contains the single access credentials) is the requisite bit.
"""

# Built-in library packages
from __future__ import annotations
# import base64
from datetime import datetime
from pathlib import Path
import shutil
# from typing import List

# Third party packages

# In-project modules
from phibes.crypto import create_crypt
# from phibes.crypto import get_crypt
from phibes.lib import phibes_file
from phibes.lib.config import ConfigModel
from phibes.lib.errors import PhibesConfigurationError
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
    if storage_path is None:
        raise PhibesConfigurationError('missing store_path')
    if locker_id is None:
        locker_path = storage_path
    else:
        locker_path = storage_path / locker_id
    return locker_path


def get_locker_file(locker_id: str = None) -> Path:
    """Convenience function for getting path to an item"""
    return get_locker_path(locker_id=locker_id) / LOCKER_FILE


def get_item_file(item_id: str, locker_id: str = None) -> Path:
    """Convenience function for getting path to an item"""
    return get_locker_path(locker_id=locker_id) / f"{item_id}.{FILE_EXT}"


def can_create(locker_path: Path, remove_if_empty=True) -> bool:
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


class LockerFileStorage(StorageImpl):

    @staticmethod
    def get(locker_id: str = None) -> dict:
        """
        Get a stored Locker from file
        @param locker_id: The optional locker_id of the locker
        @return: LockerFileStorage instance
        """
        locker_path = get_locker_path(locker_id=locker_id)
        lf = get_locker_file(locker_id=locker_id)
        if not lf.exists():
            raise PhibesNotFoundError
        else:
            rec = phibes_file.read(lf)
            rec['lock_file'] = lf
            rec['path'] = locker_path
        return rec

    @staticmethod
    def create(password: str, crypt_id: str, locker_id: str = None):
        """
        Create a Locker object
        :param password: Password for the new locker
        :param crypt_id: ID of the crypt_impl to create
        :param locker_id: The optional name of the locker.
                          Must be unique in storage
        """
        storage_path = Path(ConfigModel().store_path)
        if locker_id:
            storage_path = storage_path / locker_id
            try:
                storage_path.mkdir(exist_ok=False)
            except FileExistsError as err:
                raise PhibesExistsError(err)
        if not can_create(storage_path, remove_if_empty=False):
            raise ValueError(f"could not create {storage_path}")
        try:
            LockerFileStorage.get(locker_id=locker_id)
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
        return LockerFileStorage.get(locker_id=locker_id)

    @staticmethod
    def delete(locker_id: str = None) -> None:
        """
        Delete a locker
        @param locker_id:
        """
        item_ids = LockerFileStorage.list_items(locker_id=locker_id)
        if item_ids:
            raise PhibesExistsError(
                f'locker {locker_id} is not empty: {item_ids}'
            )
        # Delete the locker file
        get_locker_file(locker_id=locker_id).unlink()
        # Delete the locker folder if it is a named one for the locker
        if locker_id:
            shutil.rmtree(
                get_locker_path(locker_id=locker_id),
                ignore_errors=False  # don't delete a non-empty dir
            )

    @staticmethod
    def get_item(item_id: str, locker_id: str = None) -> dict:
        """
        Attempts to find and return a named item in the locker.
        Raises an exception of item isn't found
        @param item_id: ID of item - encryption of the item_name
        @param locker_id: ID of locker - hash of the locker locker_id
        @return: the item dict
        """
        item_path = get_item_file(
            item_id=item_id, locker_id=locker_id
        )
        if item_path.exists():
            return phibes_file.read(item_path)
        else:
            raise PhibesNotFoundError(f"{item_id} not found")

    @staticmethod
    def list_items(locker_id: str = None) -> list:
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

    @staticmethod
    def save_item(
            item_id: str,
            item_rec: dict,
            locker_id: str = None,
            replace: bool = False
    ) -> None:
        """
        Saves the item to the locker
        @param item_id: Encrypted item locker_id
        @param item_rec: contents of item
        @param locker_id: Optional hashed locker locker_id
        @param replace: Whether this is replacing an existing item
        @return: None
        """
        try:
            LockerFileStorage.get_item(item_id=item_id, locker_id=locker_id)
            if not replace:
                raise PhibesExistsError(f"{locker_id}:{item_id} exists")
        except PhibesNotFoundError as err:
            if replace:
                raise err
        item_path = get_item_file(item_id=item_id, locker_id=locker_id)
        phibes_file.write(
            pth=item_path,
            salt=item_rec['salt'],
            crypt_id=item_rec['crypt_id'],
            timestamp=item_rec['timestamp'],
            body=item_rec['_ciphertext'],
            overwrite=replace
        )

    @staticmethod
    def delete_item(item_id: str, locker_id: str = None) -> None:
        """
        Saves the item to the locker
        @param item_id: Encrypted item locker_id
        @param locker_id: Optional hashed locker locker_id
        @return: None
        """
        get_item_file(item_id=item_id, locker_id=locker_id).unlink()
