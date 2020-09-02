"""
Implementation of Schema

A Schema is used to enforce format on other entities, like Tags.
"""

# Built-in library packages

# Third party packages

# In-project modules
from phibes.lib.crypto import CryptImpl
from phibes.model import Item


class Schema(Item):

    def __init__(self, crypt_obj: CryptImpl, name: str, content: str = ""):
        super().__init__(crypt_obj, name, content)
        return
