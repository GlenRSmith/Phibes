"""
Implementation of CLI Item

Item is a base class for things to be stored in a Locker.
"""

# Built-in library packages

# Third party packages

# In-project modules
from lib.crypto import CryptFileWrap, get_name_hash, encrypt


FILE_EXT = "cry"

ITEM_TYPES = {
    'secret': {
        'item_dir': 'secrets'
    },
    'tag': {
        'item_dir': 'tags'
    },
    'template': {
        'item_dir': 'templates'
    },
    'schema': {
        'item_dir': 'schemata'
    }
}


class Item(object):
    """
    Storage content of a Locker
    """

    def __init__(self, locker, name, item_type):
        self.locker = locker
        self.item_type = item_type
        self.name = name
        self.content = None
        self.conf = ITEM_TYPES[item_type]
        self.crypto_file = None
        return

    def __str__(self):
        ret_val = "Item\n"
        ret_val += f"type: {self.item_type}\n"
        ret_val += f"name: {self.name}\n"
        ret_val += f"content: {self.content}\n"
        return ret_val

    @classmethod
    def create(
            cls, locker, name, item_type, content=None
    ):
        inst = cls(locker, name, item_type)
        inst.crypto_file = CryptFileWrap.create(
            inst.get_cipher_file(), locker.crypt_key, crypt_arg_is_key=True
        )
        if bool(content):
            inst.set_content(content)
        return inst

    @classmethod
    def create_and_save(
            cls,
            locker,
            name,
            item_type,
            content,
            save_plain_text=False,
            save_encrypted=True
    ):
        inst = cls(locker, name, item_type)
        inst.set_content(content)
        inst.crypto_file = CryptFileWrap.create(
            inst.get_cipher_file(), locker.crypt_key, crypt_arg_is_key=True
        )
        inst.save(
            overwrite=False,
            save_plain_text=save_plain_text,
            save_encrypted=save_encrypted
        )
        return inst

    @classmethod
    def find(cls, locker, name, item_type):
        inst = Item(locker, name, item_type)
        if inst.exists():
            inst.crypto_file = CryptFileWrap.find(inst.get_cipher_file())
            # The crypt key is shared from the locker to its items
            inst.crypto_file.key = locker.get_crypt_key()
            inst.content = inst.crypto_file.get_plaintext()
        else:
            return None
        return inst

    def save_cipher_from_text(self, overwrite=False):
        """
        Method to read from plaintext file and overwrite crypt file
        :return:
        """
        self.read_plaintext()
        self.crypto_file.set_plaintext(self.content)
        self.crypto_file.write(overwrite=overwrite)
        return

    def save_text_from_cipher(self):
        return

    def get_hash_name(self):
        return get_name_hash(self.name)

    def exists(self):
        """

        :return: Bool of whether an item matching the instance is stored
        """
        return self.get_plain_file().exists() or self.get_cipher_file().exists()

    def get_path(self):
        return self.locker.path.joinpath(
            f"{self.conf.get('item_dir')}"
        )

    def get_plain_file(self):
        plain_file_name = self.name + ".PLAINTEXT"
        return self.get_path().joinpath(f"{plain_file_name}")

    def get_cipher_file(self):
        salt, encrypted_name = encrypt(
            self.locker.crypt.key,
            self.name,
            iv=bytes.fromhex(self.locker.crypt.salt)
        )
        return self.get_path().joinpath(f"{encrypted_name}")

    # def read_encrypted(self):
    #     self.crypt.read()
    #     self.cipher_text = self.crypt.get_ciphertext()
    #     self.content = self.crypt.get_plaintext()
    #     return

    def read_plaintext(self):
        with open(self.get_plain_file(), 'r') as pf:
            self.content = pf.read()
        return

    def set_content(self, content):
        self.content = content
        self.crypto_file.set_plaintext(content)
        return

    def write_encrypted(self, overwrite):
        """
        Writes the encrypted Item to disk
        :param overwrite:
        :return:
        """
        # Make sure the crypto file's ciphertext is updated to reflect plain
        self.crypto_file.set_plaintext(self.content)
        # Then save
        self.crypto_file.write(overwrite=overwrite)
        return

    def save(
            self, overwrite=False, save_plain_text=False, save_encrypted=True
    ):
        if not save_plain_text and not save_encrypted:
            raise ValueError(
                f"Item {self.name} wasn't saved because save_* were False!"
            )
        if self.crypto_file.path.exists() and not overwrite:
            raise FileExistsError(f"Item {self.name} is already stored!")
        if self.content is None:
            raise ValueError(
                f"The item {self.name} requires some content!"
            )
        if save_plain_text:
            with open(self.get_plain_file(), 'w') as pf:
                pf.write(self.content)
        if save_encrypted:
            self.write_encrypted(overwrite=overwrite)
        return
