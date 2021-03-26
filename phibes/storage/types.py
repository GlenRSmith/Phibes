"""
Provides access to available storage types
"""

import enum

from phibes.storage.file_storage import LockerFileStorage
from phibes.storage.memory_storage import MemoryStorage


class StoreType(enum.Enum):

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = str(args[0])
        return obj

    def __init__(self, name, impl_class):
        self.impl_class = impl_class

    FileSystem = 'FileSystem', LockerFileStorage
    Memory = 'Memory', MemoryStorage


DEFAULT_STORE_TYPE = StoreType.FileSystem
