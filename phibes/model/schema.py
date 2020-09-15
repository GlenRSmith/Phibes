"""
Implementation of Schema

A Schema is used to enforce format on other entities, like Tags.
"""

# Built-in library packages

# Third party packages

# In-project modules
from phibes.crypto.crypt_ifc import CryptIfc
from phibes.model import Item


class Schema(Item):

    def __init__(self, crypt_obj: CryptIfc, name: str, content: str = ""):
        super().__init__(crypt_obj, name, content)
        return
