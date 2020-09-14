"""
A Factory is a source of crypt/hash implementations.
All available implementations are registered and accessible by name.
"""
# Built-in library packages
from __future__ import annotations
# import abc
from typing import Optional

# Third party packages

# In-project modules
from phibes.crypto import crypt_ifc
# from phibes.lib.errors import PhibesAuthError, PhibesConfigurationError
# from phibes.lib.errors import PhibesNotFoundError, PhibesExistsError


class SingletonMeta(type):
    """
    This is a metaclass (hence derived from `type`).
    A class that uses this as its metaclass can only have one instance created.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                SingletonMeta, cls
            ).__call__(*args, **kwargs)
        return cls._instances[cls]


class CryptFactory(object, metaclass=SingletonMeta):
    """
    Further extending: the callables registered here are supposed
    to return an object that implements the CryptIfc.
    That could be a function that returns an instance,
    the __init__ of a CryptIfc class, or an instance of a 'factory'
    class that has a __call__ method that returns a CryptIfc object
    """
    _default = None

    def __init__(self):
        self._objects = {}
        return

    def _create(self, key: str, **kwargs: dict):
        """
        Return the result of invoking the named-registered builder with
        the keyword arguments. This method and any other methods on this
        class should remain transparent to those parameters specific to
        creating the targets, hence the kwargs.
        @param key: The unique registered name of the desired builder
        @type key: str
        @param kwargs: params to be passed to the callable
        @type kwargs: dict
        @return: result of call
        @rtype: Any
        """
        item = self._objects.get(key)
        if not item:
            raise ValueError(f"No registered item found with {key=}")
        return item(**kwargs)

    def register_builder(self, key, builder):
        self._objects[key] = builder
        if not self._default:
            # TODO make a more intentional way to set default.
            self._default = key

    def list_builders(self):
        """
        Convenience method to inspect the registered builders
        @return: registered builders
        @rtype: list
        """
        return list(self._objects.keys())

    def create(self, password: str, crypt_id: str = None, **kwargs):
        """
        Get a registered crypt while creating a locker
        password, {type-specific args}
        Pack usage-specific params into a dict;
        e.g. `key_rounds` is specific to PBKF2 hashing
        @param password: user-provided creation password
        @type password: str
        @param crypt_id: usually omitted key for entry in factory
        @type crypt_id: str
        @param kwargs: params specific to the type of crypt being created
        @type kwargs: dict
        @return: Crypt
        @rtype: crypt_ifc.CryptIfc
        """
        # print(f"CryptFactory.create {kwargs=}")
        # print(f"CryptFactory.create {self._default=}")
        target_id = (self._default, crypt_id)[bool(crypt_id)]
        return self.get(target_id, password, None, None, **kwargs)

    def get(self, crypt_id, password, pw_hash, salt, **kwargs):
        """
        Called to get a registered crypt initialized with the given
        params (i.e. after reading the lock file).
        @param crypt_id: Registered GUID of the crypt needed
        @type crypt_id: str
        @param password: user-provided password
        @type password: str
        @param pw_hash: restored authentication hash from the created locker
        @type pw_hash: str
        @param salt: salt used to create auth hash (and encryption key)
        @type salt: str
        @param kwargs:
        @type kwargs:
        @return: Crypt
        @rtype: crypt_ifc.CryptIfc
        """
        # print(f"CryptFactory.get {kwargs=}")
        builder = self._objects.get(crypt_id)
        # print(f"CryptFactory builder {builder}")
        if not builder:
            raise ValueError(crypt_id)
        # Return the result of `__call__` on the registered item
        return builder(password, pw_hash, salt, **kwargs)


class CryptWrapper(object):

    def __init__(self, crypt_class, init_kwargs):
        self.crypt_id = crypt_class.__name__ + ''.join(
            [f"{k}{v}" for (k, v) in init_kwargs.items()]
        )
        self.crypt_class = crypt_class
        crypt_ifc.CryptIfc.validate_child(crypt_class)
        self.init_kwargs = init_kwargs
        CryptFactory().register_builder(self.crypt_id, self)
        return

    def __call__(
            self,
            password: str,
            pw_hash: Optional[str] = None,
            salt: Optional[str] = None,
            **kwargs: dict
    ):
        instance = self.crypt_class(
            password, pw_hash, salt, **self.init_kwargs
        )
        instance.crypt_id = self.crypt_id
        return instance


def register_crypt(crypt_class, unique_kw_args):
    CryptWrapper(crypt_class, unique_kw_args)


def create_crypt(password: str, crypt_id: str = None, **kwargs):
    return CryptFactory().create(password, crypt_id, **kwargs)


def get_crypt(crypt_id, password, pw_hash, salt, **kwargs):
    return CryptFactory().get(crypt_id, password, pw_hash, salt, **kwargs)


def list_crypts():
    return CryptFactory().list_builders()
