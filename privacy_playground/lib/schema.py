"""
Implementation of Schema

A Schema is used to enforce format on other entities, like Tags.
"""

# Built-in library packages

# Third party packages

# In-project modules
from . item import Item


class Schema(Item):

    def __init__(self, key: str, name: str, content: str = ""):
        super().__init__(key, name, content)
        return
