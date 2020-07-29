"""
A Locker is a storage unit for user secrets (passwords, etc.)
A Locker is represented by a file "<name>.lck" on the local file system.
A Locker has other data on the file system, but that file
(which contains the single access credentials) is the requisite bit.
"""

# Built-in library packages
import shutil

# Third party packages

# In-project modules
from .config import Config
from .crypto import authenticate_password, CryptFileWrap
from .crypto import get_name_hash, get_password_hash
from .crypto import encrypt, decrypt
from .item import FILE_EXT, Item


class Locker(object):

    @property
    def salt(self):
        """
        Convenience accessor to crypt.salt
        :return:
        """
        return self.crypt.salt

    def __init__(self, name):
        """
        A Locker object can be constructed in two scenarios:
        - client code is creating a new, empty locker
          - this method should create the locker on disk
        - client code is opening an interface to an existing locker
          - this method should try to open the locker on disk
        :param name: The name of the locker. Must be unique in storage
        """
        # key will be the symmetrical encryption key
        # It is derived from the main password, but wouldn't have to be.
        self.crypt_key = None
        # TODO: should this be abstracted to "confirm installed" or something?
        self.conf = Config()
        self.conf.assure_users_dir()
        if self.conf.hash_locker_names:
            self.path = self.conf.users_path.joinpath(get_name_hash(name))
        else:
            self.path = self.conf.users_path.joinpath(name)
        self.lock_file = self.path.joinpath(".locker.cfg")
        self.crypt = None
        return

    @classmethod
    def create_and_save(cls, name, password):
        inst = cls(name)
        if not Locker.can_create(inst.path):
            raise ValueError(f"could not create {name}")
        inst.path.mkdir(exist_ok=False)
        inst.crypt = CryptFileWrap.create(
            inst.lock_file, password, crypt_arg_is_key=False
        )
        inst.crypt.plaintext = get_password_hash(
            password, inst.crypt.salt
        ).hex()
        inst.crypt.write()
        inst.crypt_key = inst.crypt.key
        return inst

    @classmethod
    def delete(cls, name, password):
        inst = Locker.find(name, password)
        if inst:
            shutil.rmtree(inst.path)

    @classmethod
    def find(cls, name, password):
        """
        Find and return the matching locker
        :param name: Plaintext name of locker
        :param password: Locker password
        :return:
        """
        # create a Locker instance
        inst = cls(name)
        # try to find a matching locker file there
        inst.crypt = CryptFileWrap.find(inst.lock_file)
        # test whether the provided password "works" with the found file
        authenticate_password(
            password, inst.crypt.ciphertext, inst.crypt.salt
        )
        # associate the successful password's key with the locker and its file
        inst.crypt.set_crypt_key(password)
        inst.crypt_key = inst.crypt.key
        return inst

    def get_crypt_key(self):
        return self.crypt.key

    @classmethod
    def can_create(cls, locker_path, remove_if_empty=True):
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
            if bool(locker_path.glob('*')):
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

    def decrypt(self, ciphertext):
        """
        Convenience method to decrypt using a Locker object
        :param ciphertext:
        :return:
        """
        return decrypt(
            self.crypt_key, bytes.fromhex(self.salt), ciphertext
        )

    def encrypt(self, plaintext):
        """
        Convenience method to encrypt using a Locker object
        :param plaintext:
        :return:
        """
        iv, ciphertext = encrypt(
            self.crypt_key, plaintext, iv=bytes.fromhex(self.salt)
        )
        return ciphertext

    def list_items(self, item_type=None):
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
