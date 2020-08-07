"""
EmptyLocker class used by several tests for setup, teardown
"""

# Standard library imports

# Related third party imports

# Local application/library specific imports
from privacy_playground.lib.item import Item
from privacy_playground.lib.locker import Locker


class EmptyLocker(object):

    my_locker = None
    locker_name = "my_locker"
    password = "StaplerRadioPersonWomanMan"

    def setup_method(self):
        try:
            if Locker(self.locker_name, self.password):
                Locker.delete(self.locker_name, self.password)
        except FileNotFoundError:
            pass
        finally:
            self.my_locker = Locker(
                self.locker_name, self.password, create=True
            )
        return

    def teardown_method(self):
        Locker.delete(self.locker_name, self.password)
        return


class PopulatedLocker(EmptyLocker):

    def setup_method(self):
        super(PopulatedLocker, self).setup_method()
        for item_type in self.my_locker.registered_items.keys():
            content = (
                f"here is some stuff"
                f"password: HardHat"
                f"{item_type}:{item_type}_name"
            )
            pth = self.my_locker.get_item_path(
                f"{item_type}", f"{item_type}_name"
            )
            new_item = Item(
                self.my_locker.crypt_key,
                f"{item_type}_name"
            )
            new_item.content = content
            new_item.save(pth)
        return

    def teardown_method(self):
        return
