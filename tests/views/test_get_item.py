"""
pytest module for view:get_locker
"""

# Standard library imports

# Related third party imports
import pytest

# Local application/library specific imports
from phibes.lib.errors import PhibesNotFoundError
from phibes.lib.views import get_item
from phibes.model import Locker

# Local test imports
from tests.lib.test_helpers import PopulatedLocker


class TestGetItem(PopulatedLocker):
    """
    Test the get_locker view function
    """

    missing_item_name = 'do_not_get_this'

    def custom_setup(self, tmp_path):
        super(TestGetItem, self).custom_setup(tmp_path)

    def custom_teardown(self, tmp_path):
        super(TestGetItem, self).custom_teardown(tmp_path)
        try:
            Locker.delete(password=self.password, locker_name=self.locker_name)
        except PhibesNotFoundError:
            pass

    @pytest.mark.positive
    def test_get_item(self, tmp_path, datadir, setup_and_teardown):
        inst = get_item(
            password=self.password,
            locker_name=self.locker_name,
            item_name=self.common_item_name
        )
        assert inst
        assert type(inst) is dict
        for fv in inst.values():
            assert self.my_locker.crypt_impl.key not in fv
        assert inst['body'] == self.content
        for locker_name, lck in self.lockers.items():
            inst = get_item(
                password=self.password,
                locker_name=self.locker_name,
                item_name=self.common_item_name
            )
            assert inst
            assert type(inst) is dict
            for fv in inst.values():
                assert lck.crypt_impl.key not in fv
            assert inst['body'] == self.content

    @pytest.mark.negative
    def test_get_wrong_name(self, setup_and_teardown):
        with pytest.raises(PhibesNotFoundError):
            get_item(
                password=self.password,
                locker_name=self.locker_name,
                item_name=self.missing_item_name
            )
        for locker_name in self.lockers.keys():
            with pytest.raises(PhibesNotFoundError):
                get_item(
                    password=self.password,
                    locker_name=locker_name,
                    item_name=self.missing_item_name
                )
