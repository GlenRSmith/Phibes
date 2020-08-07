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
            Locker.delete(EmptyLocker.locker_name, EmptyLocker.password)
        except FileNotFoundError:
            pass
        finally:
            EmptyLocker.my_locker = Locker(
                EmptyLocker.locker_name, EmptyLocker.password, create=True
            )
        return

    def teardown_method(self):
        Locker.delete(EmptyLocker.locker_name, EmptyLocker.password)
        return


class PopulatedLocker(object):

    my_locker = None
    locker_name = "full_locker"
    password = "StaplerRadioPersonWomanMan"

    def setup_method(self):
        try:
            Locker.delete(EmptyLocker.locker_name, EmptyLocker.password)
        except FileNotFoundError:
            pass
        finally:
            PopulatedLocker.my_locker = Locker(
                PopulatedLocker.locker_name,
                PopulatedLocker.password,
                create=True
            )
            for item_type in PopulatedLocker.my_locker.registered_items.keys():
                content = (
                    f"here is some stuff"
                    f"password: HardHat"
                    f"{item_type}:{item_type}_name"
                )
                pth = PopulatedLocker.my_locker.get_item_path(
                    f"{item_type}", f"{item_type}_name"
                )
                new_item = Item(
                    PopulatedLocker.my_locker.crypt_key,
                    f"{item_type}_name"
                )
                new_item.content = content
                new_item.save(pth)
        return

    def teardown_method(self):
        Locker.delete(
            PopulatedLocker.locker_name, PopulatedLocker.password
        )
        return
