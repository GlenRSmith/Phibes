"""
pytest module for lib.locker
"""

# Standard library imports

# Related third party imports

# Local application/library specific imports
from privacy_playground.lib import locker


class TestLocker(object):

    my_locker = None
    locker_name = "my_locker"
    password = "StaplerRadioPersonWomanMan"

    def setup_method(self):
        try:
            if locker.Locker.find(
                    TestLocker.locker_name, TestLocker.password
            ):
                locker.Locker.delete(
                    TestLocker.locker_name, TestLocker.password
                )
        except:
            pass

    def teardown_method(self):
        locker.Locker.delete(TestLocker.locker_name, TestLocker.password)

    def test_good(self, tmp_path, datadir):
        print(f"Create locker")
        new_locker = locker.Locker(
            TestLocker.locker_name, TestLocker.password, create=True
        )
        print(f"Locker created {new_locker.path}")
        return


