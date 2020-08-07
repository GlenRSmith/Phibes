"""
Implementation of Template

A Template is an entry in a Locker.
"""

# Built-in library packages

# Third party packages

# In-project modules
from . item import Item


class Template(Item):

    def __init__(self, key: str, name: str, content: str = ""):
        super().__init__(key, name, content)
        return
