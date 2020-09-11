"""
A Factory is a source of crypt/hash implementations.
All available implementations are registered and accessible by name.
"""

# Built-in library packages
from __future__ import annotations
import abc
# from typing import List, Optional, Tuple

# Third party packages

# In-project modules
from . crypt_ifc import CryptIfc
# from phibes.lib.errors import PhibesAuthError, PhibesConfigurationError
# from phibes.lib.errors import PhibesNotFoundError, PhibesExistsError


class SingletonMeta(type):
    """
    This is a metaclass (hence derived from `type`).
    A class that uses this as its metaclass can only have one instance created.
    """

    # TODO: will this consider the same class imported differently to be
    # the same class? e.g. Locker vs. locker.Locker
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                SingletonMeta, cls
            ).__call__(*args, **kwargs)
        return cls._instances[cls]


class ObjectFactory(object, metaclass=SingletonMeta):
    """
    This singleton class is used to register any objects.
    They are called `builders` because they are callable, and their
    callables are intended to return newly-created objects.
    """

    def __init__(self):
        self._objects = {}
        return

    def register_object(self, key, object_arg):
        self._objects[key] = object_arg

    def list_objects(self):
        """
        Convenience method to inspect the registered objects
        @return: registered objects
        @rtype: list
        """
        return list(self._objects.keys())


class CallableFactory(ObjectFactory):
    """
    First layer of extension, expects the registered items
    to be __callable__, and calls them when accessed
    """

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


class CryptFactory(CallableFactory):
    """
    Further extending: the callables registered here are supposed
    to return an object that implements the CryptIfc.
    That could be a function that returns an instance,
    the __init__ of a CryptIfc class, or an instance of a 'factory'
    class that has a __call__ method that returns a CryptIfc object
    """
    _default = None

    def register_builder(self, key, builder):
        self.register_object(key, builder)
        if not self._default:
            # TODO make a more intentional way to set default.
            self._default = key

    def list_builders(self):
        return self.list_objects()

    def create(self, password, **kwargs):
        # This method is called to get a registered crypt when only the
        # password is known (i.e. creating a locker).
        #
        # password, {type-specific args}
        # packing our usage-specific params into a dict so the ObjectFactory
        # can remain agnostic. It also permits the callables to have varied
        # signatures.
        print(f"CryptFactory.create {kwargs=}")
        print(f"CryptFactory.create {self._default=}")
        builder = self._objects.get(self._default)
        if not builder:
            raise ValueError(self._default)
        return builder(password, **kwargs)
        # return self._create(crypt_id, **kwargs)

    # It's ok to have context position params but only the consistent ones
    # For example, if the hash method becomes Argon2, "rounds" isn't a thing.
    def get(self, crypt_id, password, pw_hash, salt, **kwargs):
        # This method is called to get a registered crypt
        # when the params are known (i.e. after reading the lock file).
        #
        """
        Get a Crypt implementation matching the service_id, initialized with
        the passed parameters.
        If no service_id is passed, the default implementation is returned.
        Clients should call this, and never the _create method from the parent.
        @param password:
        @type password:
        @param crypt_id:
        @type crypt_id:
        @return:
        @rtype:
        """
        # packing our usage-specific params into a dict so the ObjectFactory
        # can remain agnostic. It also permits the callables to have varied
        # signatures.
        # kwargs = {'password': password, 'salt': salt}
        # kwargs = {'password': password}
        print(f"CryptFactory.get {kwargs=}")
        builder = self._objects.get(crypt_id)
        if not builder:
            raise ValueError(crypt_id)
        # Not returning the thing that was registered,
        # Returning the result of `__call__` on that thing
        ret_val = builder(password, pw_hash, salt, **kwargs)
        return ret_val
        # return builder(password, salt, **kwargs)
        # return self._create(crypt_id, **kwargs)
