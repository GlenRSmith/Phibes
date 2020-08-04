"""
LockerHelper class used by several tests for setup, teardown
"""

# Standard library imports

# Related third party imports

# Local application/library specific imports
from privacy_playground.lib.locker import Locker


class LockerHelper(object):

    my_locker = None
    locker_name = "my_locker"
    password = "StaplerRadioPersonWomanMan"

    def setup_method(self):
        try:
            Locker.delete(LockerHelper.locker_name, LockerHelper.password)
        except FileNotFoundError:
            pass
        finally:
            LockerHelper.my_locker = Locker(
                LockerHelper.locker_name, LockerHelper.password, create=True
            )
        return

    def teardown_method(self):
        Locker.delete(LockerHelper.locker_name, LockerHelper.password)
        return


