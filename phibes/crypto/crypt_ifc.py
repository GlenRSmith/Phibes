"""
Interface definition for crypt/hash-ing classes
"""
# Built-in library packages
import abc
from typing import Optional

# Third party packages

# In-project modules


class HashIfc(abc.ABC):

    @abc.abstractmethod
    def __init__(self, **kwargs):
        pass

    @abc.abstractmethod
    def hash_str(
            self, plaintext: str, salt: str, rounds: int, length_bytes: int
    ) -> str:
        pass


class EncryptionIfc(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def create_salt(cls):
        pass

    @property
    @abc.abstractmethod
    def key(self):
        pass

    @key.setter
    @abc.abstractmethod
    def key(self, new_key):
        pass

    @abc.abstractmethod
    def __init__(self, key: str, salt: Optional[str] = None, **kwargs):
        pass

    @abc.abstractmethod
    def encrypt(self, plaintext: str, salt: str) -> str:
        pass

    @abc.abstractmethod
    def decrypt(self, ciphertext: str, salt: str) -> str:
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

    @abc.abstractmethod
    def __init__(
            self,
            password: str,
            pw_hash: Optional[str] = None,
            salt: Optional[str] = None,
            **kwargs: dict
    ):
        """
        Common constructor for all Crypt classes
        @param password: User password, will always be passed
        @type password: str
        @param pw_hash: Previously-stored hash, passed for existing items
        @type pw_hash: str
        @param salt: Previously-stored salt, passed for existing items
        @type salt: str
        @param kwargs: additional parameters required by certain Crypt classes
        @type kwargs: dict
        """
        pass

    @abc.abstractmethod
    def encrypt(self, plaintext: str, salt: Optional[str] = None) -> str:
        pass

    @abc.abstractmethod
    def decrypt(self, ciphertext: str, salt: Optional[str] = None) -> str:
        pass

    # @abc.abstractmethod
    # def encrypt_password(
    #         self, password: str, salt: Optional[str] = None
    # ) -> str:
    #     pass

    @abc.abstractmethod
    def hash_name(
            self,
            name: str,
            salt: Optional[str] = None
    ) -> str:
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


def class_has_callable(
        cls,
        method,
        abstract: Optional[bool] = None
):
    is_abs = "__isabstractmethod__"
    return (
        hasattr(cls, method)
        and callable(getattr(cls, method))
        and (
            not abstract
            or (
                hasattr(getattr(cls, method), is_abs)
                and getattr(getattr(cls, method), is_abs)
            )
        )
        and (
            abstract is None
            or abstract
            or (
                not hasattr(getattr(cls, method), is_abs)
                or not getattr(getattr(cls, method), is_abs, True)
            )
        )
    )
