"""
Storage-only model classes
"""

# Built-in library packages
from datetime import datetime

# Third party packages
# In-project modules
from phibes.crypto import default_id
from phibes.lib.config import ConfigModel as Config
from phibes.lib.errors import PhibesUnknownError
from phibes.storage.types import StoreType


class Model(object):
    """
    Base class for storage models
    """

    def __init__(self, locker_id: str = None, **kwargs):
        config = Config()
        store_type = StoreType(config.store['store_type'])
        self.storage = store_type.impl_class(
            locker_id=locker_id, **config.store
        )


class LockerModel(Model):
    """
    Model class for Locker, only storage operations
    """

    def __init__(self, locker_id: str = None, **kwargs):
        """
        valid signatures have kwargs that include:
        1: create - pw_hash, salt, crypt_id, locker_id, timestamp
        2: get - locker_id
        In both cases, locker_id can be None for singleton
        """
        super().__init__(locker_id, **kwargs)
        self.locker_id = locker_id
        if {'pw_hash', 'salt'}.issubset(kwargs.keys()):
            self.storage.create(
                pw_hash=kwargs['pw_hash'],
                salt=kwargs['salt'],
                crypt_id=kwargs.get('crypt_id', default_id)
            )
        # should storage should also be "getting" in initialization?
        rec = self.storage.get()
        self.pw_hash = rec['body']
        self.salt = rec['salt']
        self.crypt_id = rec['crypt_id']
        self.locker_id = self.locker_id
        self.timestamp = rec['timestamp']

    def delete(self):
        """
        Delete a Locker instance from storage
        """
        try:
            return self.storage.delete()
        except Exception as err:
            raise PhibesUnknownError(
                f'{err=}\n'
                f'{self.storage=}'
            )

    def create_item(
            self,
            item_id: str,
            content: str,
            timestamp: str = str(datetime.now())
    ):
        return ItemModel(
            locker_id=self.locker_id,
            item_id=item_id,
            salt=self.salt,
            crypt_id=self.crypt_id,
            timestamp=timestamp,
            content=content
        ).create()

    def update_item(
            self,
            item_id: str,
            content: str,
            timestamp: str = str(datetime.now())
    ):
        return ItemModel(
            locker_id=self.locker_id,
            item_id=item_id,
            salt=self.salt,
            crypt_id=self.crypt_id,
            timestamp=timestamp,
            content=content
        ).update()

    def delete_item(self, item_id: str):
        return ItemModel(locker_id=self.locker_id, item_id=item_id).delete()

    def get_item(self, item_id: str):
        return self.storage.get_item(item_id=item_id)

    def get_items(self):
        return self.storage.list_items()


class ItemModel(Model):
    """
    Model class for Item, only storage operations
    """

    def __init__(self, locker_id: str = None, **kwargs):
        super().__init__(locker_id, **kwargs)
        self.locker_id = locker_id
        self.item_id = kwargs.get('item_id', None)
        self.salt = kwargs.get('salt', None)
        self.crypt_id = kwargs.get('crypt_id', None)
        self.timestamp = kwargs.get('timestamp', str(datetime.now()))
        self.body = kwargs.get('content', None)

    def save(self, update: bool):
        """
        Save the Item
        """
        item_rec = {
            'salt': self.salt,
            'crypt_id': self.crypt_id,
            'timestamp': self.timestamp,
            '_ciphertext': self.body,
        }
        return self.storage.save_item(
            item_id=self.item_id,
            item_rec=item_rec,
            replace=update
        )

    def create(self):
        """
        Create and save the Item
        """
        return self.save(update=False)

    def update(self):
        """
        Update the Item
        """
        return self.save(update=True)

    def delete(self):
        """
        Delete the Item
        """
        return self.storage.delete_item(item_id=self.item_id)
