"""
A Factory is a source of crypt/hash implementations.
All available implementations are registered and accessible by name.
"""
# Built-in library packages
from __future__ import annotations
from typing import Optional, Type

# Third party packages

# In-project modules
from phibes.crypto import crypt_ifc
from phibes.lib.errors import PhibesConfigurationError
from phibes.lib.utils import validate_child


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
        self._default_crypt_id = None
        return

    def register_wrapper(
            self,
            key: str,
            wrapper: CryptWrapper,
            fallback_id: Optional[str] = None,
            is_default: bool = False
    ):
        """
        Store in memory an instance of CryptWrapper referenced by a unique key
        :param key: unique identifier (crypt_id)
        :param wrapper: instance of CryptWrapper to store
        :param fallback_id:
            optional registered ID of crypt to use if this one fails @runtime
        :param is_default: If True, sets this crypt_id as default
        :return: None
        """
        if is_default and self._default_crypt_id:
            raise PhibesConfigurationError(
                f"Can't set {key} as default crypt_id "
                f"{self._default_crypt_id} is already registered as default"
            )
        if self._objects.get(key, None):
            raise ValueError(f"{key} already registered")
        self._objects[key] = wrapper
        self._fallbacks[key] = fallback_id
        if is_default:
            self._default_crypt_id = key

    def list_wrappers(self) -> list:
        """
        Convenience method to inspect the registered wrappers
        :return: registered wrappers
        """
        ret_val = list(self._objects.keys())
        if None in ret_val:
            ret_val.remove(None)
        return ret_val

    def list_fallbacks(self) -> list:
        """
        Convenience method to inspect the registered wrappers' fallbacks
        :return: registered wrappers' fallbacks
        """
        return list(self._fallbacks.keys())

    def create(
            self, password: str, crypt_id: str = None, **kwargs
    ) -> crypt_ifc.CryptIfc:
        """
        Returns a registered crypt e.g. to the locker creation process
        :password: user-provided creation password
        :crypt_id: usually omitted key for entry in factory
        :kwargs: params specific to the type of crypt being created
        e.g. `key_rounds` is specific to PBKF2 hashing
        :return: Crypt
        """
        crypt_id = (crypt_id, self._default_crypt_id)[crypt_id is None]
        ret_ob = None
        while not ret_ob:
            try:
                wrapper = self._objects.get(crypt_id)
                if not wrapper:
                    raise ValueError(crypt_id)
                return wrapper(crypt_id, password, **kwargs)
            except ValueError:
                try:
                    next_id = self._fallbacks[crypt_id]
                except KeyError as err:
                    raise KeyError(f"{crypt_id} {err}")
                if next_id is None:
                    break
                crypt_id = next_id
        msg = f"Error retrieving {crypt_id} - availa: {self.list_wrappers()}"
        raise ValueError(msg)

    def get(
            self,
            crypt_id: str,
            password: str,
            pw_hash: str,
            salt: str,
            **kwargs
    ) -> crypt_ifc.CryptIfc:
        """
        Returns the crypt (via the wrapper object) initialized with the
        given params (i.e. after reading the lock file).
        :crypt_id: Registered GUID of the crypt needed
        :password: user-provided password
        :pw_hash: restored authentication hash from the created locker
        :salt: salt used to create auth hash (and encryption key)
        :kwargs:
        :return: Crypt
        """
        wrapper = self._objects.get(crypt_id)
        if not wrapper:
            raise ValueError(crypt_id)
        return wrapper(crypt_id, password, pw_hash, salt, **kwargs)


class CryptWrapper(object):
    """
    Container entity that allows storage of references to all CryptIfc
    implementations while allowing late instantiation of them
    """

    def __init__(
            self,
            crypt_class: Type,
            fallback_id: str = None,
            is_default: bool = False,
            **init_kwargs
    ):
        """
        Construct a CryptWrapper instance
        :crypt_class: class that implements CryptIfc
        :fallback_id: id of crypt to use if creation of this fails at runtime
        :param init_kwargs: kwargs to pass to c'tor of `crypt_class`
        """
        # autogenerate the unique crypt_id
        self.crypt_id = crypt_class.__name__ + ''.join(
            [f"{k}{v}" for (k, v) in init_kwargs.items()]
        )
        self.crypt_class = crypt_class
        # as early as possible, validate `crypt_class` fulfills CryptIfc
        validate_child(crypt_ifc.CryptIfc, crypt_class)
        # keeps the init_kwargs to pass to `crypt_class` c'tor
        self.init_kwargs = init_kwargs
        CryptFactory().register_wrapper(
            self.crypt_id, self, fallback_id, is_default
        )
        return

    def __str__(self):
        return (
            f"{self.crypt_id=}\n"
            f"{self.crypt_class=}\n"
            f"{self.init_kwargs=}\n"
        )

    def __call__(
            self,
            crypt_id: str,
            password: str,
            pw_hash: Optional[str] = None,
            salt: Optional[str] = None,
            **kwargs: dict
    ):
        """
        Constructs and returns an instance of the actual CryptIfc class
        :param crypt_id: unique registered identifier of the crypt
        :param password: user-provided password
        :param pw_hash: if provided, a restored hash used to auth the password
        :param salt: the salt that was used to generate the pw_hash
        :param kwargs: constructor params specific to the select implementation
        :return: instance of class that implements CryptIfc
        """
        return self.crypt_class(
            crypt_id, password, pw_hash, salt, **self.init_kwargs
        )


def register_crypt(
        crypt_class, fallback_id=None, is_default=False, **unique_kw_args
):
    """
    Register a CryptIfc implementation instance
    :param crypt_class: CryptIfc child class
    :param fallback_id: Registered crypt_id to use if this one fails at runtime
    :param unique_kw_args: dict of kwargs to use when creating this instance
    :param is_default: bool indicating whether this is the default crypt
    :return: the crypt_id for the newly-registered crypt
    """
    return CryptWrapper(
        crypt_class, fallback_id, is_default, **unique_kw_args
    ).crypt_id


def register_default_crypt(crypt_class, fallback_id=None, **unique_kw_args):
    """
    Register a CryptIfc implementation instance as the default to use
    when creating new Lockers
    :param crypt_class: CryptIfc child class
    :param fallback_id: Registered crypt_id to use if this one fails at runtime
    :param unique_kw_args: dict of kwargs to use when creating this instance
    :return: the crypt_id for the newly-registered crypt
    """
    return register_crypt(
        crypt_class, fallback_id=fallback_id, is_default=True, **unique_kw_args
    )


def create_crypt(password: str, crypt_id: str = None, **kwargs):
    """
    Returns an instance of the CryptIfc registered to the `crypt_id`
    by creating a new instance. If no `crypt_id` is provided, the default
    crypt (or its fallback) will be returned.
    :param password: User password
    :param crypt_id: registered Crypt unique string
    :return:
    """
    return CryptFactory().create(password, crypt_id)


def get_crypt(crypt_id, password, pw_hash, salt, **kwargs):
    """
    Returns an instance of the CryptIfc registered to the `crypt_id`
    by getting an instance - password authentication is performed
    :param crypt_id: registered Crypt unique string
    :param password: User password
    :param pw_hash: restored value from a Locker
    :param salt: restored value from a Locker
    :return:
    """
    return CryptFactory().get(crypt_id, password, pw_hash, salt)


def list_crypts() -> list:
    """
    Returns a list of the `crypt_id`s of all registered crypts
    """
    return CryptFactory().list_wrappers()
