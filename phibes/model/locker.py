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
from typing import List, Optional, Tuple

# Third party packages

# In-project modules
from phibes.crypto import create_crypt, get_crypt
from phibes.lib import phibes_file
from phibes.lib.config import ConfigModel
from phibes.lib.errors import PhibesAuthError, PhibesConfigurationError
from phibes.lib.errors import PhibesNotFoundError, PhibesExistsError
from phibes.model import FILE_EXT, Item
# pylint: disable=unused-import
# Item subclasses must be loaded so __subclasses__ below will report them
from . schema import Schema
from . secret import Secret
from . tag import Tag
from . template import Template

registered_items = {}
for sub in [Schema, Secret, Tag, Template]:
    registered_items[sub.get_type_name()] = sub

for cls in Item.__subclasses__():
    if cls.get_type_name() not in registered_items:
        registered_items[cls.get_type_name()] = cls


ItemList = List[Item]
# HEX_REGEX = "^(0[xX])?[A-Fa-f0-9]+$"
# HexStr = Match[HEX_REGEX]
# str(type(self)).split("'")[1].split(".")[-1].lower()

LOCKER_FILE = ".config"


def find_matching_crypt_impl(path: Path, plain_name, password):
    msgs = f"{path=}\n"
    msgs += f"{plain_name=}\n"
    dirs = [s.name for s in path.glob('*') if s.is_dir()]
    msgs += f"{dirs=}\n"
    plain_dir = (None, path.joinpath(plain_name))[plain_name in dirs]
    msgs += f"{plain_dir=}\n"
    plain_crypt_inst = None
    had_auth_failure = False
    if plain_dir:
        dirs.remove(plain_name)
        lockfile = plain_dir / LOCKER_FILE
        if lockfile.exists():
            plain_rec = phibes_file.read(lockfile)
            try:
                msgs += f"trying to get {plain_rec['crypt_id']=}\n"
                plain_crypt_inst = get_crypt(
                    plain_rec['crypt_id'],
                    password,
                    plain_rec['body'],
                    plain_rec['salt']
                )
            except PhibesAuthError:
                had_auth_failure = True
    hashed_crypt_inst = None
    # We don't know the name hash until after we confirm the crypt impl
    # so just pick up every directory that has a lock file in it
    found_lockfiles = {
        flf: path.joinpath(flf, LOCKER_FILE)
        for flf in dirs
        if path.joinpath(flf, LOCKER_FILE).exists()
    }
    for flf in found_lockfiles:
        msgs += f"looking for lock file {found_lockfiles[flf].resolve()}\n"
        rec = phibes_file.read(found_lockfiles[flf])
        pw_hash = rec['body']
        salt = rec['salt']
        crypt_id = rec['crypt_id']
        try:
            msgs += f"trying to get crypt {crypt_id=} {password=} {pw_hash=}\n"
            crypt_inst = get_crypt(crypt_id, password, pw_hash, salt)
        except PhibesAuthError:
            had_auth_failure = True
            continue
        # auth succeeded in the c'tor, but check the dirname, too
        if crypt_inst.hash_name(plain_name) == flf:
            hashed_crypt_inst = crypt_inst
            break
    if hashed_crypt_inst and plain_crypt_inst:
        raise PhibesConfigurationError(
            f"lock file conflict: {hashed_crypt_inst} {plain_crypt_inst}"
        )
    elif hashed_crypt_inst:
        return hashed_crypt_inst
    elif plain_crypt_inst:
        return plain_crypt_inst
    elif had_auth_failure:
        raise PhibesAuthError(f"could not auth {path} {plain_name}\n{msgs}")
    else:
        raise PhibesNotFoundError(f"no match: {path} {plain_name}\n{msgs}")


class Locker(object):

    registered_items = registered_items

    def __init__(self, name: str, password: str, create: bool = False):
        """
        A Locker object can be constructed in two scenarios:
        - client code is creating a new, empty locker
          - this method should create the locker on disk
        - client code is opening an interface to an existing locker
          - this method should try to open the locker on disk
        :param name: The name of the locker. Must be unique in storage
        """
        self.conf = ConfigModel()
        if create:
            self.crypt_impl = create_crypt(password)
        else:
            self.crypt_impl = find_matching_crypt_impl(
                self.conf.store_path, name, password
            )
        plain_path = self.conf.store_path.joinpath(name)
        hash_dir = self.crypt_impl.hash_name(name)
        hash_path = self.conf.store_path.joinpath(hash_dir)
        # clean up empty dirs to reduce conflict check complexity
        if plain_path.exists() and not any(plain_path.iterdir()):
            shutil.rmtree(plain_path)
        if hash_path.exists() and not any(hash_path.iterdir()):
            shutil.rmtree(hash_path)
        # TODO provide a merge capability?
        if hash_path.exists() and plain_path.exists():
            raise PhibesExistsError(
                f"Locker {name} conflict problem!!!\n"
                f"Storage path {self.conf.store_path} contains both\n"
                f"- {plain_path}\n"
                f"- {hash_path}\n"
            )
        plain_lock = plain_path / LOCKER_FILE
        hash_lock = hash_path / LOCKER_FILE
        if self.conf.hash_locker_names:
            self.path = hash_path
        else:
            self.path = plain_path
        self.lock_file = self.path.joinpath(LOCKER_FILE)
        if not create:
            err_msg = ""
            if self.conf.hash_locker_names:
                if plain_path.exists():
                    err_msg += f"Config hash_locker_names is True while\n"
                    err_msg += f"plain locker {plain_path.resolve()} exists\n"
            else:
                if hash_path.exists():
                    err_msg += f"Config hash_locker_names is False while\n"
                    err_msg += f"hashed locker {hash_path.resolve()} exists\n"
            if err_msg:
                raise PhibesConfigurationError(
                    f"Error reading Locker {name}\n{err_msg}\n"
                    f"{self.conf}"
                )
            if not self.lock_file.exists():
                tmp_dir = self.conf.store_path / hash_dir
                tmp_file = tmp_dir / LOCKER_FILE
                if tmp_file.exists():
                    self.path = self.conf.store_path / hash_dir
                    self.lock_file = self.path / LOCKER_FILE
                else:
                    raise PhibesNotFoundError(
                        f"Locker {self.conf.store_path / name} not found\n"
                        f"Did you mean to pass create=True?"
                    )
            rec = phibes_file.read(self.lock_file)
            self._timestamp = rec['timestamp']
            self.crypt_impl = get_crypt(
                crypt_id=rec["crypt_id"],
                password=password,
                pw_hash=rec["body"],
                salt=rec["salt"]
            )
        else:
            err_msg = ""
            if plain_path.exists():
                if self.conf.hash_locker_names:
                    err_msg += "Can't create hashed dir, unhashed exists\n"
                if plain_lock.exists():
                    err_msg += f"lock file {plain_lock.resolve()} exists\n"
                else:
                    err_msg += f"locker dir {plain_path.resolve()} exists\n"
            if hash_path.exists():
                if not self.conf.hash_locker_names:
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
                    f"{self.conf}"
                )
            if not Locker.can_create(self.path):
                raise ValueError(f"could not create {name}")
            self.crypt_impl = create_crypt(password)
            self.path.mkdir(exist_ok=False)
            phibes_file.write(
                self.lock_file,
                self.crypt_impl.salt,
                self.crypt_impl.crypt_id,
                self.crypt_impl.encrypt(str(datetime.now())),
                self.crypt_impl.pw_hash,
                overwrite=False
            )
        return

    @classmethod
    def delete(cls, name: str, password: str):
        try:
            inst = Locker(name, password)
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
            inst = Locker(name, password, create=False)
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

    def encode_item_name(
            self, item_type: str, item_name: str
    ) -> str:
        """
        Encode and encrypt the item type and name into the
        encrypted file name used to store Items.

        :param item_type: Item type
        :param item_name: Item name
        :return: Fully encoded/encrypted file name
        """
        if item_type not in self.registered_items:
            raise ValueError(
                f"{item_type} not registered: {self.registered_items}"
            )
        type_enc = self.encrypt(item_type)
        name_enc = self.encrypt(item_name)
        encrypted_name = self.encrypt(f"{type_enc}:{name_enc}")
        return f"{encrypted_name}.{FILE_EXT}"

    def decode_item_name(
            self, file_name: str
    ) -> Tuple[str, str]:

        """
        Convert from encrypted, encoded filename format on disk
        and return the item type and name used to create the filename.

        :param file_name:
        :return:
        """
        # Tolerate with or without file extension
        if file_name.endswith(f".{FILE_EXT}"):
            file_name = file_name[0:-4]
        type_enc, name_enc = self.decrypt(file_name).split(':')
        item_type = self.decrypt(type_enc)
        item_name = self.decrypt(name_enc)
        return item_type, item_name

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

    def get_item_path(self, item_type: str, item_name: str) -> Path:
        file_name = self.encode_item_name(item_type, item_name)
        return self.path.joinpath(file_name)

    def create_item(
            self, item_name: str,
            item_type: str,
            template_name: Optional[str] = None
    ) -> Item:
        item_cls = registered_items[item_type]
        new_item = item_cls(self.crypt_impl, item_name)
        if template_name:
            template = self.get_item(template_name, "template")
            if not template:
                raise PhibesNotFoundError(
                    f"template {template_name} not found"
                )
            new_item.content = template.content
        return new_item

    def add_item(self, item: Item) -> None:
        pth = self.get_item_path(item.item_type, item.name)
        item.save(pth, overwrite=False)
        return

    def get_item(self, item_name: str, item_type: str) -> Optional[Item]:
        pth = self.get_item_path(item_type, item_name)
        if pth.exists():
            item_cls = registered_items[item_type]
            found_item = item_cls(self.crypt_impl, item_name)
            found_item.read(pth)
            # TODO: validate using salt
        else:
            raise PhibesNotFoundError(
                f"{item_type}:{item_name} not found"
            )
        return found_item

    def update_item(self, item: Item) -> None:
        pth = self.get_item_path(item.item_type, item.name)
        item.save(pth, overwrite=True)
        return

    def delete_item(self, item_name: str, item_type: str) -> None:
        self.get_item_path(item_type, item_name).unlink()

    def list_items(self, item_type=None) -> ItemList:
        """
        Return a list of Items of the specified type in this locker
        :param item_type: type of Items (e.g. Secret) to list, None = all
        :return:
        """
        if item_type:
            if type(item_type) is set:
                item_type = list(item_type)
            if type(item_type) is not list:
                item_type = [item_type]
            missing_types = []
            for it in item_type:
                if it not in registered_items:
                    missing_types.append(it)
            if missing_types:
                raise ValueError(
                    f"{missing_types} not found in {registered_items}")
        else:
            item_type = registered_items
        items = []
        item_gen = self.path.glob(f"*.{FILE_EXT}")
        for item_path in [it for it in item_gen]:
            inst_type, inst_name = self.decode_item_name(item_path.name)
            if inst_type:
                if inst_type not in registered_items:
                    raise ValueError(f"{item_type} is not a valid item type")
                else:
                    if inst_type in item_type:
                        found = self.get_item(inst_name, inst_type)
                        items.append(found)
        return items

    def find_all(self, item_type_filter=None, filter_include=True):
        """
        Find matching items in a locker
        Default invocation returns all items.
        :param item_type_filter: list of item types to include/exclude
        :param filter_include: whether item_type_filter is `include` or exclude
        :return: list of matching items
        """
        if not item_type_filter and not filter_include:
            raise ValueError(f"You are asking to exclude all item types!")
        if not item_type_filter:
            item_type_filter = set(Locker.registered_items)
        else:
            if type(item_type_filter) is set:
                pass
            if type(item_type_filter) is list:
                item_type_filter = set(item_type_filter)
            elif type(item_type_filter) is str:
                item_type_filter = {item_type_filter}
            else:
                raise TypeError(
                    f"unexpected arg type {type(item_type_filter)}"
                )
        if not item_type_filter <= set(Locker.registered_items):
            unknown_types = item_type_filter - set(Locker.registered_items)
            raise ValueError(
                f"{unknown_types} not found in {set(Locker.registered_items)}")
        if not filter_include:
            item_type_filter = set(Locker.registered_items) - item_type_filter
        items = self.list_items(item_type_filter)
        return items
