"""
Implementation of Secrets

A Secret is an entry in a Locker.
"""

# Built-in library packages

# Third party packages

# In-project modules
from phibes.crypto.crypt_ifc import CryptIfc
from phibes.model import Item


class Secret(Item):

    def __init__(self, crypt_obj: CryptIfc, name: str, content: str = ""):
        super().__init__(crypt_obj, name, content)
        return
