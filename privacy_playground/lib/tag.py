"""
Implementation of Tags

A Tag is an Item whose content is a list of items
"""

# Built-in library packages
from __future__ import annotations
import json
from typing import List, Set

# Third party packages

# In-project modules
from . item import Item


ItemSet = Set[Item]
ItemList = List[Item]


class Tag(Item):
    """
    A tag is a name and list of items.
    """

    def __init__(self, locker, name, create: bool = False):
        """
        Create or find a matching tag in the locker
        :param locker: Locker to use
        :param name: name of Tag
        :param create: whether to create a new Tag
        """
        super().__init__(locker, name, 'tag', create=create)
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

    def __str__(self):
        """
        Override of default object __str__ method
        :return:
        """
        data = dict()
        data['items'] = list(self.content)
        return json.dumps(data, indent=4)
