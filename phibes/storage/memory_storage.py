"""
In-memory storage implementation (for demo/development only)
"""
# Built-in library packages
from datetime import datetime

from phibes.crypto import default_id
from phibes.lib.errors import PhibesExistsError
from phibes.lib.errors import PhibesNotFoundError
from phibes.storage.storage_impl import StorageImpl


mock_lockers = {}


class MemoryStorage(StorageImpl):
    """
    This is currently a demo-only class, used to store lockers and items
    in memory for the duration of a scripted run.
    """

    def __init__(self, locker_id: str = None, **kwargs):
        super(MemoryStorage, self).__init__(**kwargs)
        self.locker_id = locker_id

    def get(self) -> dict:
        """
        Get an existing Locker record from memory
        """
        try:
            rec = mock_lockers[self.locker_id]
        except KeyError as err:
            raise PhibesNotFoundError(
                f'{err=}\n'
                f'{mock_lockers.keys()=}'
            )
        return rec

    def create(
            self, pw_hash: str, salt: str, crypt_id: str = default_id
    ):
        global mock_lockers
        if self.locker_id in mock_lockers:
            raise PhibesExistsError(f'locker {self.locker_id} already exists')
        mock_lockers[self.locker_id] = {
            "crypt_id": crypt_id,
            "body": pw_hash,
            "salt": salt,
            "timestamp": str(datetime.now()),
            "items": {}
        }

    def delete(self):
        global mock_lockers
        try:
            del mock_lockers[self.locker_id]
        except KeyError as err:
            raise PhibesNotFoundError(
                f'{err=}\n'
                f'{mock_lockers=}'
            )
        return

    def get_item(self, item_id: str):
        try:
            return mock_lockers[self.locker_id]['items'][item_id]
        except KeyError as err:
            raise PhibesNotFoundError(
                f'{err=}\n'
                f'{mock_lockers=}'
            )

    def list_items(self):
        try:
            return mock_lockers[self.locker_id]['items']
        except KeyError as err:
            raise PhibesNotFoundError(
                f'{err=}\n'
                f'{mock_lockers=}'
            )

    def save_item(
            self, item_id: str, item_rec: dict, replace: bool = False
    ):
        exists = item_id in mock_lockers[self.locker_id]['items']
        if exists:
            if not replace:
                raise PhibesExistsError(
                    f'{item_id=} already exists in {self.locker_id=}'
                )
        else:
            if replace:
                raise PhibesNotFoundError(
                    f'{item_id=} does not exist in {self.locker_id=}'
                )
        mock_lockers[self.locker_id]['items'][item_id] = {
            'salt': item_rec['salt'],
            'crypt_id': item_rec['crypt_id'],
            'timestamp': item_rec['timestamp'],
            'body': item_rec['_ciphertext']
        }
        return mock_lockers[self.locker_id]['items'][item_id]

    def create_item(
            self,
            item_id: str,
            salt: str,
            crypt_id: str,
            timestamp: str,
            body: str
    ):
        rec = {
            'salt': salt,
            'crypt_id': crypt_id,
            'timestamp': timestamp,
            'body': body
        }
        return self.save_item(item_id=item_id, item_rec=rec, replace=False)

    def update_item(
            self,
            item_id: str,
            salt: str,
            crypt_id: str,
            timestamp: str,
            body: str
    ):
        rec = {
            'salt': salt,
            'crypt_id': crypt_id,
            'timestamp': timestamp,
            'body': body
        }
        return self.save_item(item_id=item_id, item_rec=rec, replace=True)

    def add_item(self, item_id: str, item_rec: dict) -> None:
        return self.save_item(item_id, item_rec)

    def delete_item(self, item_id: str):
        exists = item_id in mock_lockers[self.locker_id]['items']
        if not exists:
            raise PhibesNotFoundError(
                f'{item_id=} does not exist in {self.locker_id=}'
            )
        del mock_lockers[self.locker_id]['items'][item_id]
