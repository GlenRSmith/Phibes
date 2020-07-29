"""
Implementation of Secrets

A Secret is an entry in a Locker.
"""

# Built-in library packages

# Third party packages

# In-project modules
from lib.item import Item

KEY_BYTES = 32
SALT_BYTES = 16


class Secret(Item):

    @classmethod
    def find(cls, locker, name):
        return super(Secret, cls).find(
            locker, name, 'secret'
        )

    def __init__(
            self, locker, name, content=None
    ):
        super().__init__(locker, name, 'secret')
        return
