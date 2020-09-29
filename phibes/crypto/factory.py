"""
A Factory is a source of crypt/hash implementations.
All available implementations are registered and accessible by name.
"""
# Built-in library packages
from __future__ import annotations
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

    def __init__(self):
        self._objects = {}
        self._fallbacks = {}
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

    def register_builder(self, key, builder, fallback_id=None):
        if self._objects.get(key, None):
            raise ValueError(f"{key} already registered")
        self._objects[key] = builder
        self._fallbacks[key] = fallback_id

    def list_builders(self):
        """
        Convenience method to inspect the registered builders
        @return: registered builders
        @rtype: list
        """
        ret_val = list(self._objects.keys())
        if None in ret_val:
            ret_val.remove(None)
        return ret_val

    def list_fallbacks(self):
        """
        Convenience method to inspect the registered builders' fallbacks
        @return: registered builders' fallbacks
        @rtype: list
        """
        return list(self._fallbacks.keys())

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
        if crypt_id is None:
            crypt_id = self._fallbacks[crypt_id]
        ret_ob = None
        while not ret_ob:
            try:
                ret_ob = self.get(crypt_id, password, None, None, **kwargs)
                return ret_ob
            except Exception as err:
                try:
                    next_id = self._fallbacks[crypt_id]
                except KeyError as err:
                    raise KeyError(f"{crypt_id} {err}")
                if next_id is None:
                    break
                crypt_id = next_id
        return ret_ob

    def get(
            self, crypt_id, password,
            pw_hash: Optional[str], salt: Optional[str],
            **kwargs
    ):
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
        builder = self._objects.get(crypt_id)
        if not builder:
            raise ValueError(crypt_id)
        # Return the result of `__call__` on the registered item
        return builder(password, pw_hash, salt, **kwargs)


class CryptWrapper(object):

    def __init__(self, crypt_class, fallback_id=None, **init_kwargs):
        self.crypt_id = crypt_class.__name__ + ''.join(
            [f"{k}{v}" for (k, v) in init_kwargs.items()]
        )
        self.crypt_class = crypt_class
        crypt_ifc.CryptIfc.validate_child(crypt_class)
        self.init_kwargs = init_kwargs
        CryptFactory().register_builder(self.crypt_id, self, fallback_id)
        return

    def __str__(self):
        return (
            f"{self.crypt_id=}\n"
            f"{self.crypt_class=}\n"
            f"{self.init_kwargs=}\n"
        )

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


def register_crypt(crypt_class, fallback_id=None, **unique_kw_args):
    return CryptWrapper(crypt_class, fallback_id, **unique_kw_args).crypt_id


def register_default_crypt(crypt_class, fallback_id=None, **unique_kw_args):
    default_id = register_crypt(
        crypt_class, fallback_id=fallback_id, **unique_kw_args
    )
    CryptFactory().register_builder(
        key=None, builder=None, fallback_id=default_id
    )
    return default_id


def create_crypt(password: str, crypt_id: str = None, **kwargs):
    return CryptFactory().create(password, crypt_id, **kwargs)


def get_crypt(crypt_id, password, pw_hash, salt, **kwargs):
    return CryptFactory().get(crypt_id, password, pw_hash, salt, **kwargs)


def list_crypts():
    return CryptFactory().list_builders()
