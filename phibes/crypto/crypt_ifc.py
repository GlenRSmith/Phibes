"""
Interface definition for crypt/hash-ing classes
"""
# Built-in library packages
import abc
from typing import Iterator, Optional

# Third party packages

# In-project modules


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

    # @abc.abstractmethod
    # def authenticate(self, password: str) -> bool:
    #     pass

    @classmethod
    def validate_child(cls, subclass):
        required_methods = abstract_methods(cls)
        missing_methods = []
        for rm in required_methods:
            if (
                    hasattr(subclass, rm) and
                    hasattr(getattr(subclass, rm),'__isabstractmethod__') and
                    getattr(subclass, rm).__isabstractmethod__ and
                    callable(getattr(subclass, rm))
            ):
                pass
            else:
                missing_methods.append(rm)
        ret_val = True
        for rm in required_methods:
            ret_val &= (
                    hasattr(subclass, rm) and
                    callable(getattr(subclass, rm))
            )
        return missing_methods

    @classmethod
    def __subclasshook__(cls, subclass):
        ret_val = True
        for rm in abstract_methods(cls):
            ret_val &= class_has_callable(subclass, rm)
        return ret_val


def class_has_callable(
        cls,
        method,
        abstract: Optional[bool] = None
):
    is_abs = "__isabstractmethod__"
    return (
        hasattr(cls, method) and
        callable(getattr(cls, method)) and
        (
            not abstract or
            (
                hasattr(getattr(cls, method), is_abs) and
                getattr(getattr(cls, method), is_abs)
            )
        ) and
        (
            abstract is None or
            abstract or
            (
                not hasattr(getattr(cls, method), is_abs) or
                not getattr(getattr(cls, method), is_abs, False)
            )
        )
    )


def abstract_methods(cls) -> Iterator[str]:
    ret_list = []
    for attr_name in dir(cls):
        if class_has_callable(cls, attr_name, abstract=True):
            ret_list.append(attr_name)
    return iter(ret_list)


def r_issubof_l(cls, sub):
    return all(
        class_has_callable(sub, am, abstract=False)
        for am in abstract_methods(cls)
    )
