"""
Implementation of Tags

A Tag is an Item whose content is a list of items
"""

# Built-in library packages
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Set

# Third party packages

# In-project modules
from phibes.crypto.crypt_ifc import CryptIfc
from phibes.model import Item


ItemSet = Set[Item]
ItemList = List[Item]


class Tag(Item):
    """
    A tag is a name and list of items.
    """

    def __init__(self, crypt_obj: CryptIfc, name: str, content: str = ""):
        """
        Create or find a matching tag in the locker
        :param key: Encryption key
        :param name: name of Tag
        :param content: optional content
        """
        super().__init__(crypt_obj, name, content)
        # if there is existing content, it will be applied during read
        self.content = set()
        return

    @property
    def content(self) -> ItemSet:
        """
        Property accessor that takes the unencrypted text returned by
        the accessor on the parent (Item) class, and further processes
        by converting that text to a set object
        :return: set of items associated with this Tag
        """
        if not super(Tag, self).content:
            rat_val = set()
        else:
            rat_val = set(json.loads(super(Tag, self).content))
        return rat_val

    @content.setter
    def content(self, value: ItemSet):
        """
        Property setter that turns a set of Items into a serialized (str)
        list before passing to the parent (Item) class to be encrypted
        :param value: set of items to assign to content
        :return:
        """
        super(Tag, self.__class__).content.__set__(
            self, json.dumps(list(value))
        )

    def add_item(self, item: Item):
        """
        Adds an item to this tag's referred item set.
        :param item:
        :return:
        """
        tmp = self.content
        tmp.add(f"{item.item_type}:{item.name}")
        self.content = tmp
        # this won't work:
        # self.content.add(secret.name)
        # self.content gets a copy here, and the add is only applied to that
        return

    def add_items(self, items: ItemSet):
        """
        Adds a set of Items to this Tag's referred item set.
        :param items:
        :return:
        """
        tmp = self.content.union(items)
        self.content = tmp
        return

    def remove_item(self, item: Item):
        """
        Removes an Item from this Tag's set of Items.
        :param item:
        :return:
        """
        tmp = self.content
        tmp.remove(f"{item.item_type}:{item.name}")
        self.content = tmp
        return

    def list_items(self) -> ItemList:
        """
        Returns a list from the set of Items associated with this Tag.
        :return:
        """
        return list(self.content)

    def save(self, pth: Path, overwrite=False):
        super().save(pth, overwrite=overwrite)
        return

    def __str__(self):
        """
        Override of default object __str__ method
        :return:
        """
        data = dict()
        data['items'] = list(self.content)
        return json.dumps(data, indent=4)
