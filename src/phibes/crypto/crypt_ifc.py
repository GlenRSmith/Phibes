"""
Interface definition for crypt classes
"""
# Built-in library packages
import abc
from typing import Optional

# Third party packages

# In-project modules
from phibes.lib.errors import PhibesAuthError
from phibes.lib.utils import class_has_callable


class CryptIfc(abc.ABC):
    """
    Interface definition for encryption classes
    These encompass hashing and encryption
    """

    salt_length_bytes = -1

    @property
    def salt(self):
        return self._salt

    @salt.setter
    def salt(self, new_salt: str):
        salt = (new_salt, self.create_salt())[new_salt is None]
        if len(bytes.fromhex(salt)) != self.salt_length_bytes:
            raise ValueError(
                f"salt {new_salt} is {len(bytes.fromhex(salt))} bytes long\n"
                f"{self.salt_length_bytes} bytes required\n"
            )
        self._salt = salt

    @classmethod
    @abc.abstractmethod
    def create_salt(cls):
        """
        Creates and returns a salt suitable for this implementation
        """
        pass

    def __init__(
            self,
            crypt_id: str,
            password: str,
            pw_hash: Optional[str] = None,
            salt: Optional[str] = None,
            **kwargs
    ):
        """
        Common constructor for all Crypt classes
        A CryptIfc instance is created/gotten when a locker is created/gotten.
        Like the Locker, it is created using just the password,
        and gotten using the password, and the pw_hash & salt from the locker.
        :param crypt_id: unique registered ID for this crypt
        :param password: User password
        :param pw_hash: Previously-stored hash, passed for existing items
        :param salt: Previously-stored salt, passed for existing items
        :param kwargs: additional parameters required by certain Crypt classes
        """
        if bool(pw_hash) ^ bool(salt):
            pref = f"{self.__class__.__name__}\n"
            raise ValueError(
                f"invalid call to __init__\n"
                f"valid calls are are:\n"
                f"{pref}(password)\n"
                f"{pref}(password, pw_hash, salt)\n"
                f"{password=} {pw_hash=} {salt=} {kwargs=}"
            )
        self.crypt_id = crypt_id
        self.salt = (self.create_salt(), salt)[bool(salt)]
        self.key = self.create_key(password, self.salt)
        self.pw_hash = self.hash_pw(password)
        if pw_hash and not (self.pw_hash == pw_hash):
            raise PhibesAuthError(
                f"{pw_hash} does not match {self.pw_hash}"
            )
        return

    def hash_pw(self, password: str) -> str:
        """
        Hash the password
        :param password: the password
        :return: the hash
        """
        return self.encrypt(self.hash_name(password, self.salt))

    @abc.abstractmethod
    def create_key(self, password: str, salt: str):
        """
        Create an encryption key suitable for this implementation
        :param password: User password to start
        :param salt: Salt to mix in
        :return: Encryption key
        """
        pass

    @abc.abstractmethod
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypts the plaintext with the salt
        :param plaintext: str to encrypt
        :return: encrypted value
        """
        pass

    @abc.abstractmethod
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt the ciphertext
        :param ciphertext: encrypted text
        :return: Original plaintext
        """
        pass

    @abc.abstractmethod
    def hash_name(self, name: str, salt: str) -> str:
        pass

    @classmethod
    def __subclasshook__(cls, subclass):
        parent_abstract_methods = {
            name for name in dir(cls)
            if class_has_callable(cls, name, abstract=True)
        }
        child_concrete_methods = {
            name for name in dir(cls)
            if class_has_callable(subclass, name, abstract=False)
        }
        return parent_abstract_methods.issubset(
            child_concrete_methods
        )
