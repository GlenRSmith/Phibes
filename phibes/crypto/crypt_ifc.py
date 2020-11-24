"""
Interface definition for crypt/hash-ing classes
"""
# Built-in library packages
import abc
from typing import Optional

# Third party packages

# In-project modules
from phibes.lib.errors import PhibesAuthError
from phibes.lib.utils import class_has_callable


class HashIfc(abc.ABC):
    """
    Interface definition for hash classes
    """

    @abc.abstractmethod
    def __init__(self, **kwargs):
        """
        Signature definition for constructing a HashIfc
        In each implementation, kwargs should contain parameters
        that will be held constant for a specific registered strategy.
        For example, for PBKDF2, the fact that SHA256 would be a property
        of a registered strategy, and not something passed (and possibly
        changed to e.g. SHA128) for each item being hashed.
        These kwargs and their values become part of the name of the
        registered strategy.
        That does not preclude them from being stored with the
        crypted items.
        @param kwargs:
        @type kwargs:
        """
        pass

    @abc.abstractmethod
    def hash_str(self, plaintext: str, **kwargs) -> str:
        """
        Signature definition for performing a hash on a plaintext.
        In each implementation, kwargs should contain parameters
        that may (and possibly must) vary between invocations from
        the same registered strategy.
        For example, for PBKDF2, the `salt` used when hashing a string
        should be unique for each string.
        These kwargs and their values
        @param plaintext: text to hash
        @param kwargs: keyword arguments, variable per implementation
        @return:
        """
        pass


"""

The top-level encryption/hashing class needs to expose:

* Some of the operations imply there is a salt already set,
  and that is why salt isn't enumerated on them

- create an instance with arguments:
    - password
    - password, salt
    - name, password
    - name, password, salt

- 'regular' encrypt with argument `plaintext`
- 'regular' decrypt with argument `ciphertext`
- password hashing (e.g. pbkdf2, argon2, etc.) with argument `password`
- name hashing (can just use pw hashing fwiw) with argument `plaintext`
- authentication with arguments `password`, `ciphertext`
"""


class CryptIfc(abc.ABC):
    """
    Interface definition for cryption classes
    These encompass hashing and encryption
    """

    HashType = None
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
        and gotten using the password plus
        the pw_hash and salt from the locker file.
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
        self._hasher = self.HashType(**kwargs)
        self.salt = (self.create_salt(), salt)[bool(salt)]
        self.key = self.create_key(password, self.salt)
        self.pw_hash = self.encrypt(self.hash_name(password, self.salt))
        if pw_hash and not (self.pw_hash == pw_hash):
            raise PhibesAuthError(
                f"{pw_hash} does not match {self.pw_hash}"
            )
        return

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
    def validate_child(cls, subclass):
        if not cls.__subclasshook__(subclass):
            missing = {
                name for name in dir(cls)
                if class_has_callable(cls, name, abstract=True)
            } - {
                name for name in dir(cls)
                if class_has_callable(subclass, name, abstract=False)
            }
            raise ValueError(
                f"{subclass} is missing implementation for {missing}"
            )
        return

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
