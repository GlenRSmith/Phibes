"""
Storage Implementation Interface
"""
# Built-in library packages
import abc
# from typing import Optional

# Third party packages
# In-project modules


class StorageImpl(abc.ABC):

    @abc.abstractmethod
    def __init__(self, locker_id: str = None, **kwargs):
        pass

    @abc.abstractmethod
    def get(self) -> dict:
        """
        Returns a Locker dictionary representation
        """
        pass

    @abc.abstractmethod
    def create(self, pw_hash: str, salt: str, crypt_id: str):
        """
        Stores a new Locker object
        :param pw_hash: Hashed Password for the new locker
        :param salt: Encryption salt
        :param crypt_id: ID of the locker's crypt_impl
        """
        pass

    @abc.abstractmethod
    def delete(self) -> None:
        """
        Deletes the locker
        @return:
        """
        pass

    @abc.abstractmethod
    def get_item(self, item_id: str) -> dict:
        """
        Attempts to find and return a named item in the locker.
        Raises an exception of item isn't found
        @param item_id: ID of item - encryption of the item_name
        @return: the item dict
        """
        pass

    @abc.abstractmethod
    def list_items(self) -> list:
        """
        Returns a list of Items in this locker
        :return:
        """
        pass

    @abc.abstractmethod
    def add_item(self, item_id: str, item_rec: dict) -> None:
        """
        Saves the item to the locker
        @param item_id: Item name - encrypted by caller
        @param item_rec: dict representation of item
        @return: None
        """
        pass

    @abc.abstractmethod
    def delete_item(self, item_id: str) -> None:
        """
        Deletes the item from the locker
        @param item_id: Item locker_id - encrypted by caller
        @return: None
        """
        pass
