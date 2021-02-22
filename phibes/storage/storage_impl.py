"""
Storage Implementation Interface
"""
# Built-in library packages
import abc
from typing import Optional

# Third party packages
# In-project modules


class StorageImpl(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def get(cls, locker_id: str = None) -> dict:
        """
        Returns a Locker dictionary representation
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def create(cls, password: str, crypt_id: str, name: str = None):
        """
        Creates a Locker object
        :param password: Password for the new locker
        :param crypt_id: ID of the crypt_impl to create
        :param name: The optional name of the locker. Must be unique in storage
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def delete(cls, password: str, name: str = None) -> None:
        """
        Deletes a locker
        @param password:
        @param name:
        @return:
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_item(cls, item_id: str, locker_id: str = None) -> dict:
        """
        Attempts to find and return a named item in the locker.
        Raises an exception of item isn't found
        @param item_id: ID of item - encryption of the item_name
        @param locker_id: ID of locker - hash of the locker name
        @return: the item dict
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def list_items(cls, locker_id: str = None) -> list:
        """
        Returns a list of Items in this locker
        :return:
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def add_item(
            cls, item_id: str, item_rec: dict, locker_id: str = None
    ) -> None:
        """
        Saves the item to the locker
        @param item_id: Item name - encrypted by caller
        @param item_rec: dict representation of item
        @param locker_id: Optional hashed locker name
        @return: None
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def delete_item(item_id: str, locker_id: str = None) -> None:
        """
        Deletes the item from the locker
        @param item_id: Item locker_id - encrypted by caller
        @param locker_id: Optional hashed locker locker_id
        @return: None
        """
        pass
