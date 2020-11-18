"""
A Locker is a storage unit for user secrets (passwords, etc.)
A Locker is represented by a file "<name>.lck" on the local file system.
A Locker has other data on the file system, but that file
(which contains the single access credentials) is the requisite bit.
"""

# Built-in library packages
from __future__ import annotations
from datetime import datetime
from pathlib import Path
import shutil
from typing import List, Optional

# Third party packages

# In-project modules
from phibes.crypto import create_crypt, get_crypt
from phibes.lib import phibes_file
from phibes.lib.config import ConfigModel
from phibes.lib.errors import PhibesAuthError, PhibesConfigurationError
from phibes.lib.errors import PhibesNotFoundError, PhibesExistsError
from phibes.model import FILE_EXT, Item


ItemList = List[Item]
# HEX_REGEX = "^(0[xX])?[A-Fa-f0-9]+$"
# HexStr = Match[HEX_REGEX]
# str(type(self)).split("'")[1].split(".")[-1].lower()

LOCKER_FILE = ".config"


class Locker(object):

    def __init__(self):
        """
        This should only be called by the class methods `get` and `create`
        """
        self.path = None
        self.lock_file = None
        self.crypt_impl = None
        return

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
        # create a list of all dirs immediately under the storage path
        dirs = [s.name for s in path.glob('*') if s.is_dir()]
        msgs += f"{dirs=}\n"
        had_auth_failure = False
        valid_crypts = {}
        # We don't know the name hash until after we confirm the crypt impl
        # so just pick up every directory that has a lock file in it
        found_lockfiles = {
            flf: path.joinpath(flf, LOCKER_FILE)
            for flf in dirs
            if path.joinpath(flf, LOCKER_FILE).exists()
        }
        for flf in found_lockfiles:
            msgs += f"... {found_lockfiles[flf].resolve()}\n"
            rec = phibes_file.read(found_lockfiles[flf])
            pw_hash = rec['body']
            salt = rec['salt']
            crypt_id = rec['crypt_id']
            try:
                msgs += f"trying {crypt_id=} {password=} {pw_hash=}\n"
                crypt_inst = get_crypt(crypt_id, password, pw_hash, salt)
            except PhibesAuthError:
                had_auth_failure = True
                msgs += f"auth fail {crypt_id=} {password=} {pw_hash=}\n"
                continue
            if crypt_inst.hash_name(name) == flf or name == flf:
                valid_crypts[flf] = crypt_inst
        if len(valid_crypts) == 0:
            if had_auth_failure:
                raise PhibesAuthError(f"{msgs}")
            raise PhibesNotFoundError(
                f"no matching Locker: {msgs}"
            )
        elif len(valid_crypts) > 1:
            raise PhibesConfigurationError(
                f"multiple crypts found {valid_crypts}\n{msgs}"
            )
        crypt_dir = (list(valid_crypts.keys()))[0]
        inst.crypt_impl = valid_crypts[crypt_dir]
        inst.path = path / crypt_dir
        inst.lock_file = inst.path / LOCKER_FILE
        # if configured to hash locker names, and found&authed locker
        # is in un-hashed dir, or vice versa, raise an error
        if conf.hash_locker_names == (crypt_dir == name):
            raise PhibesConfigurationError(
                f"Locker {name} does not match config\n"
                f"Valid lock path: {inst.lock_file.resolve()}\n"
                f"Hash name setting: {conf.hash_locker_names}\n"
                f"Full config: {conf}"
            )
        return inst

    @classmethod
    def create(cls, name: str, password: str, crypt_id: str = None):
        """
        Create a Locker object
        :param name: The name of the locker. Must be unique in storage
        :param password: Password for the new locker
        :param crypt_id: ID of the crypt_impl to create
        """
        conf = ConfigModel()
        inst = Locker()
        inst.crypt_impl = create_crypt(password, crypt_id)
        plain_path = conf.store_path.joinpath(name)
        hash_path = conf.store_path.joinpath(
            inst.crypt_impl.hash_name(name)
        )
        # TODO provide a merge capability?
        plain_lock = plain_path / LOCKER_FILE
        hash_lock = hash_path / LOCKER_FILE
        inst.path = (plain_path, hash_path)[conf.hash_locker_names]
        inst.lock_file = inst.path / LOCKER_FILE
        err_msg = ""
        conf_hash = conf.hash_locker_names
        if plain_path.exists() and conf_hash:
            if conf.hash_locker_names:
                err_msg += "Can't create hashed dir, unhashed exists\n"
            if plain_lock.exists():
                err_msg += f"lock file {plain_lock.resolve()} exists\n"
            else:
                err_msg += f"locker dir {plain_path.resolve()} exists\n"
        if hash_path.exists() and not conf_hash:
            if not conf.hash_locker_names:
                err_msg += "Can't create unhashed dir, hashed exists\n"
            if hash_lock.exists():
                err_msg += f"lock file {hash_lock.resolve()} exists\n"
            else:
                err_msg += f"locker dir {hash_path.resolve()} exists\n"
        if err_msg:
            raise PhibesExistsError(
                f"Error attempting to create Locker {name}\n"
                f"{err_msg} already exists\n"
                f"Did you mean to pass create=False?\n"
                f"{inst}"
            )
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

    def encode_item_name(self, item_name: str) -> str:
        """
        Encode and encrypt the item type and name into the
        encrypted file name used to store Items.

        :param item_name: Item name
        :return: Fully encoded/encrypted file name
        """
        if not item_name:
            raise ValueError(
                f"Empty or None {item_name=} not allowed"
            )
        name_enc = self.encrypt(item_name)
        return f"{name_enc}.{FILE_EXT}"

    def decode_item_name(self, file_name: str) -> str:

        """
        Convert from encrypted, encoded filename format on disk
        and return the item type and name used to create the filename.

        :param file_name:
        :return:
        """
        # Tolerate with or without file extension
        if file_name.endswith(f".{FILE_EXT}"):
            file_name = file_name[0:-4]
        item_name = self.decrypt(file_name)
        return item_name

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
        file_name = self.encode_item_name(item_name)
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
            inst_name = self.decode_item_name(item_path.name)
            found = self.get_item(inst_name)
            items.append(found)
        return items
