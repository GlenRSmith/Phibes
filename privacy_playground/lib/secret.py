"""
Implementation of Secrets

A Secret is an entry in a Locker.
"""

# Built-in library packages

# Third party packages

# In-project modules
from . item import Item


class Secret(Item):

    def __init__(self, locker, name, create: bool = False):
        super().__init__(locker, name, 'secret', create=create)
        return

    @classmethod
    def find(cls, locker, name, item_type='secret'):
        return super(Secret, cls).find(
            locker, name, 'secret'
        )

