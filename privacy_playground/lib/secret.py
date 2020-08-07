"""
Implementation of Secrets

A Secret is an entry in a Locker.
"""

# Built-in library packages

# Third party packages

# In-project modules
from . item import Item


class Secret(Item):

    def __init__(self, key: str, name: str, content: str = ""):
        super().__init__(key, name, content)
        return
