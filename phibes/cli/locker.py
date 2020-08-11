"""
This module has the local, unencrypted cache support for the Locker module.
"""

# Built-in library packages
import os

# Third party packages


# In-project modules


class Locker(object):

    def __init__(self, name, hash_name):
        """
        A Locker object can be constructed in two scenarios:
        - client code is creating a new, empty locker
          - this method should create the locker on disk
        - client code is opening an interface to an existing locker
          - this method should try to open the locker on disk
        :param name: The name of the locker. Must be unique in storage
        :param hash_name: Should the locker's name be hashed on the file system?
        """
        config.assure_users_dir()
        users_path = config.get_users_path()
        if hash_name:
            self.path = users_path.joinpath(crypto.get_name_hash(name))
        else:
            self.path = users_path.joinpath(name)
        self.lock_file = self.path.joinpath(".locker.cfg")
        self.crypt = None
        return

    @classmethod
    def get_item_types(cls):
        return list(cls.item_types.keys())

    @classmethod
    def create_and_save(cls, name, password, hash_name=True):
        inst = cls(name, hash_name=hash_name)
        if not Locker.can_create(inst.path):
            raise ValueError(f"could not create {name}")
        os.mkdir(inst.path)
        config.make_item_dirs(inst.path)
        inst.crypt = CryptFileWrap.create(
            inst.lock_file, password, crypt_arg_is_key=False
        )
        inst.crypt.set_plaintext(
            crypto.get_password_hash(password, inst.crypt.salt).hex(),
            salt=inst.crypt.salt
        )
        inst.crypt.write()
        inst.crypt_key = inst.crypt.key
        return inst

    @classmethod
    def find(cls, name, password, hash_name=True):
        inst = cls(name, hash_name=hash_name)
        inst.crypt = CryptFileWrap.find(
            inst.lock_file
        )
        authenticate_password(
            password, inst.crypt.get_ciphertext(), inst.crypt.salt
        )
        inst.crypt.set_crypt_key(password)
        inst.crypt_key = inst.crypt.key
        return inst

    def get_salt(self):
        return self.crypt.salt

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
                raise ValueError(
                    f"{locker_path} already exists and is not a directory"
                )
            if bool(locker_path.glob('*')):
                raise ValueError(
                    f"dir {locker_path} already exists and is not empty"
                )
            else:
                if remove_if_empty:
                    locker_path.rmdir()
                else:
                    return False
        return True

    def validate(self):
        if not os.path.exists(self.path):
            raise ValueError(f"Locker path {self.path} does not exist")
        if not os.path.isdir(self.path):
            raise ValueError(f"Locker path {self.path} not a directory")
        if not os.path.exists(self.lock_file):
            raise ValueError(f"Locker file {self.lock_file} does not exist")
        if not os.path.isfile(self.lock_file):
            raise ValueError(f"{self.lock_file} is not a file")

    def decrypt(self, ciphertext, salt=None):
        """
        Convenience method to decrypt using a Locker object
        :param ciphertext:
        :param salt:
        :return:
        """

        if not salt:
            salt = self.get_salt()
        return crypto.decrypt(
            self.crypt_key, bytes.fromhex(salt), ciphertext
        )

    def encrypt(self, plaintext):
        """
        Convenience method to encrypt using a Locker object
        :param plaintext:
        :return:
        """
        iv, ciphertext = crypto.encrypt(
            self.crypt_key, plaintext, iv=bytes.fromhex(self.get_salt())
        )
        return ciphertext

    def list_items(self, item_type=None):
        """
        Return a list of Items of the specified type in this locker
        :param item_type: type of Items (e.g. Secret) to list, None = all
        :return:
        """
        if item_type and item_type not in Locker.item_types:
            raise ValueError(f"{item_type} is not a valid item type")
        item_conf = Locker.item_types.get(item_type)
        item_names = []
        item_path = self.path.joinpath(item_conf['item_dir'])
        print(f"{item_path}")
        for entry in os.scandir(item_path):
            print(f"{entry}")
            if entry.is_file() and entry.name.endswith(FILE_EXT):
                print(f"{entry.name[0:-4]}")
                print(f"{self.decrypt(entry.name[0:-4]).decode()}")
                item_names.append(
                    self.decrypt(entry.name[0:-4])
                )
        return item_names

    def list_secrets(self):
        return self.list_items('secret')
        # self.validate()
        # secret_names = []
        # for entry in os.scandir(self.path):
        #     if entry.is_file() and entry.name.endswith('.sct'):
        #         secret_names.append(
        #             self.decrypt(entry.name[0:-4]).decode()
        #         )
        # return secret_names

