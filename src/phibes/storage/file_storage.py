"""
A Locker is a storage unit for user secrets (passwords, etc.)
A Locker is represented by a file "<locker_id>.lck" on the local file system.
A Locker has other data on the file system, but that file
(which contains the single access credentials) is the requisite bit.
"""

# Built-in library packages
from __future__ import annotations

from abc import ABC
from datetime import datetime
from pathlib import Path
import shutil

# Third party packages

# In-project modules
from phibes.lib import phibes_file
from phibes.lib.errors import PhibesConfigurationError
from phibes.lib.errors import PhibesExistsError
from phibes.lib.errors import PhibesNotFoundError

# In-package modules
from .storage_impl import StorageImpl


LOCKER_FILE = "locker.config"
ITEM_FILE_EXT = 'cry'
EXEMPT_FILES = ['.phibes.cfg']


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
        found = [
            i for i in locker_path.glob('*') if i.name not in EXEMPT_FILES
        ]
        if bool(found):
            raise PhibesExistsError(
                f"dir {locker_path} already exists and is not empty\n"
                f"contains {found}"
            )
        else:
            if remove_if_empty:
                locker_path.rmdir()
    return True


class LockerFileStorage(StorageImpl, ABC):

    def __init__(self, locker_id: str = None, **kwargs):
        super(LockerFileStorage, self).__init__(**kwargs)
        self.store_path = Path(kwargs['store_path'])
        self.locker_id = locker_id

    @property
    def locker_path(self):
        if self.store_path is None:
            raise PhibesConfigurationError('missing store_path')
        if self.locker_id is None:
            locker_path = self.store_path
        else:
            locker_path = self.store_path / self.locker_id
        return locker_path

    @property
    def locker_file(self):
        return self.locker_path / LOCKER_FILE

    def get(self) -> dict:
        """
        Get a stored Locker from file
        @return: LockerFileStorage instance
        """
        if not self.locker_file.exists():
            raise PhibesNotFoundError(f'file: {self.locker_file}')
        else:
            rec = phibes_file.read(self.locker_file)
            rec['lock_file'] = self.locker_file
            rec['path'] = self.locker_path
        return rec

    def create(self, pw_hash: str, salt: str, crypt_id: str) -> dict:
        """
        Create a Locker record in storage

        @param pw_hash: Hashed password, for auth, of new locker
        @param salt: Encryption salt for locker
        @param crypt_id: ID of the crypt_impl used by locker
        @return: record for newly persisted locker
        """
        self.store_path = Path(self.store_path)
        if self.locker_id:
            try:
                self.locker_path.mkdir(exist_ok=False)
            except FileExistsError as err:
                raise PhibesExistsError(err)
        else:
            if not can_create(self.locker_path, remove_if_empty=False):
                raise ValueError(f"could not create {self.locker_path}")
        try:
            self.get()
        except PhibesNotFoundError:
            pass
        phibes_file.write(
            pth=self.locker_file,
            salt=salt,
            crypt_id=crypt_id,
            timestamp=str(datetime.now()),
            body=pw_hash,
            overwrite=False
        )
        return self.get()

    def delete(self) -> None:
        """
        Delete a locker
        """
        item_ids = self.list_items()
        for id in item_ids:
            self.delete_item(item_id=id)
        # Delete the locker file
        self.locker_file.unlink()
        # Delete the locker folder if it is a named one for the locker
        if self.locker_id:
            shutil.rmtree(
                self.locker_path,
                ignore_errors=False  # don't delete a non-empty dir
            )

    def get_item(self, item_id: str) -> dict:
        """
        Attempts to find and return a named item in the locker.
        Raises an exception of item isn't found
        @param item_id: ID of item - encryption of the item_name
        @return: the item dict
        """
        item_path = self.locker_path / f"{item_id}.{ITEM_FILE_EXT}"
        if item_path.exists():
            return phibes_file.read(item_path)
        else:
            raise PhibesNotFoundError(f"{item_id} not found")

    def list_items(self) -> list:
        """
        Return a list of Items of the specified type in this locker
        :return:
        """
        items = []
        item_gen = self.locker_path.glob(f"*.{ITEM_FILE_EXT}")
        ext_len = len(ITEM_FILE_EXT) + 1
        for item_path in [it for it in item_gen]:
            stored_name = item_path.name[0:-ext_len]
            items.append(stored_name)
        return items

    def save_item(
            self, item_id: str, item_rec: dict, replace: bool = False
    ) -> None:
        """
        Saves the item to the locker
        @param item_id: Encrypted item locker_id
        @param item_rec: contents of item
        @param replace: Whether this is replacing an existing item
        @return: None
        """
        try:
            self.get_item(item_id=item_id)
            if not replace:
                raise PhibesExistsError(f"{self.locker_id}:{item_id} exists")
        except PhibesNotFoundError as err:
            if replace:
                raise err
        item_path = self.locker_path / f"{item_id}.{ITEM_FILE_EXT}"
        phibes_file.write(
            pth=item_path,
            salt=item_rec['salt'],
            crypt_id=item_rec['crypt_id'],
            timestamp=item_rec['timestamp'],
            body=item_rec['_ciphertext'],
            overwrite=replace
        )

    def add_item(self, item_id: str, item_rec: dict) -> None:
        return self.save_item(item_id, item_rec)

    def delete_item(self, item_id: str) -> None:
        """
        Saves the item to the locker
        @param item_id: Encrypted item locker_id
        @return: None
        """
        item_path = self.locker_path / f"{item_id}.{ITEM_FILE_EXT}"
        item_path.unlink()
