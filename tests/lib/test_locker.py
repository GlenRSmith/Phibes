"""
pytest module for lib.locker
"""

# Standard library imports

# Related third party imports

# Local application/library specific imports
from locker_helper import PopulatedLocker
from privacy_playground.lib.locker import Locker


class TestLocker(object):

    my_locker = None
    locker_name = "my_locker"
    password = "StaplerRadioPersonWomanMan"

    def setup_method(self):
        try:
            if Locker(TestLocker.locker_name, TestLocker.password):
                Locker.delete(TestLocker.locker_name, TestLocker.password)
        except:
            pass

    def teardown_method(self):
        Locker.delete(TestLocker.locker_name, TestLocker.password)

    def test_good(self, tmp_path, datadir):
        Locker(TestLocker.locker_name, TestLocker.password, create=True)
        found = Locker(
            TestLocker.locker_name, TestLocker.password, create=False
        )
        assert found
        return


class TestItemStuff(PopulatedLocker):

    def test_find_all(self, tmp_path, datadir):
        all = self.my_locker.find_all()
        assert all != []
        for item_type in self.my_locker.registered_items:
            item_filter = [item_type]
            items = self.my_locker.find_all(item_filter, filter_include=True)
            assert len(items) == 1
            assert items[0].item_type == item_type
        for item_type in self.my_locker.registered_items:
            item_filter = [item_type]
            items = self.my_locker.find_all(item_filter, filter_include=False)
            assert len(items) == len(self.my_locker.registered_items) - 1
            for it in items:
                assert it.item_type != item_type
        return


