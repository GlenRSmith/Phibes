"""
Implementation of Secrets

A Secret is an entry in a Locker.
"""

# Built-in library packages
import secrets

# Third party packages

# In-project modules
from lib import crypto
from lib.item import Item

KEY_BYTES = 32
SALT_BYTES = 16
FILE_EXT = 'sct'
ITEM_DIR = 'secrets'


class Secret(Item):

    @classmethod
    def find(cls, locker, name):
        return super(Secret, cls).find(
            locker, name, 'secret'
        )
        # secret_name = locker.encrypt(name)
        # secret_file = locker.path.joinpath(
        #     f"{ITEM_DIR}/{secret_name}.{FILE_EXT}"
        # )
        # if secret_file.exists():
        #     with open(f"{secret_file}", "r") as s_file:
        #         # the salt was stored in hexadecimal form, with a line feed
        #         salt = s_file.readline().strip('\n')
        #         # the next line in the file is the encrypted secret
        #         ciphertext = s_file.readline().strip('\n')
        #         plaintext = locker.decrypt(ciphertext, salt=salt).decode()
        #     return plaintext
        # else:
        #     return None

    def __init__(
            self, locker, name, content=None
    ):
        super().__init__(locker, name, 'secret')
        return

    # def __init__(self, name, locker, create=False, content=None):
    #     self.name = name
    #     self.locker = locker
    #     self.salt = None
    #     self.crypt_name = None
    #     # don't want to even expose the plaintext name
    #     self.crypt_name = self.locker.encrypt(self.name)
    #     self.path = locker.joinpath('secrets').joinpath(self.crypt_name)
    #     self.secret_file = locker.locker_path.joinpath(
    #         f"{self.crypt_name}.sct"
    #     )
    #     if create:
    #         if self.secret_file.exists():
    #             raise ValueError(f"Secret {name} already exists")
    #         if content is None:
    #             raise ValueError(f"The secret {name} requires some content!")
    #         else:
    #             # safely get random bytes, turn into string hexadecimal
    #             self.salt = secrets.token_bytes(SALT_BYTES).hex()
    #             ciphertext = self.locker.encrypt(
    #                 content, salt=self.salt
    #             )
    #             with open(self.secret_file, "w") as cipher_file:
    #                 cipher_file.write(f"{self.salt}\n{ciphertext}\n")
    #     else:
    #         if content is not None:
    #             msg = f"Secret.__init__ can't take text without create=True"
    #             details = f"{name} {content}"
    #             raise ValueError(msg + details)
    #         with open(f"{self.secret_file}", "r") as s_file:
    #             # the salt was stored in hexadecimal form, with a line feed
    #             self.salt = s_file.readline().strip('\n')
    #             # the next line in the file is the encrypted secret
    #             ciphertext = s_file.readline().strip('\n')
    #             self.plaintext = self.locker.decrypt(
    #                 ciphertext, salt=self.salt
    #             ).decode()
    #     super().__init__()
    #
    # def update(self, secret_text):
    #     """
    #     Method to overwrite an existing secret
    #     :param secret_text: new secret text to encrypt
    #     :return:
    #     """
    #     # safely get random bytes, turn into string hexadecimal
    #     self.salt = secrets.token_bytes(SALT_BYTES).hex()
    #     ciphertext = self.locker.encrypt(secret_text, salt=self.salt)
    #     with open(self.secret_file, "w") as cipher_file:
    #         cipher_file.write(f"{self.salt}\n{ciphertext}\n")
    #     return

