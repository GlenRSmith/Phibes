"""
pytest module for lib.locker
"""

# Standard library imports
from copy import copy

# Related third party imports
import pytest

# Local application/library specific imports
from phibes.lib.errors import PhibesAuthError, PhibesNotFoundError
from phibes.model import Locker

# Local test imports
from tests.lib.test_helpers import EmptyLocker, plain_texts, PopulatedLocker


class TestLocker(EmptyLocker):

    my_locker = None
    locker_name = "my_locker"
    password = "StaplerRadioPersonWomanMan"

    def custom_setup(self, tmp_path):
        super(TestLocker, self).custom_setup(tmp_path)
        try:
            if Locker.get(self.locker_name, self.password):
                Locker.delete(self.locker_name, self.password)
        except Exception:
            pass

    def custom_teardown(self, tmp_path):
        super(TestLocker, self).custom_teardown(tmp_path)
        try:
            Locker.delete(self.locker_name, self.password)
        except PhibesNotFoundError:
            pass

    @pytest.mark.positive
    def test_good(self, tmp_path, datadir, setup_and_teardown):
        Locker.create(self.locker_name, self.password)
        found = Locker.get(self.locker_name, self.password)
        assert found
        return


class TestItemStuff(PopulatedLocker):

    @pytest.mark.positive
    def test_find_all(self, tmp_path, datadir, setup_and_teardown):
        all_lockers = list(self.lockers.values()) + [self.my_locker]
        for lck in all_lockers:
            all = lck.find_all()
            assert all != []
            for item_type in lck.registered_items:
                item_filter = [item_type]
                items = lck.find_all(item_filter, filter_include=True)
                assert len(items) == 1
                assert items[0].item_type == item_type
            for item_type in lck.registered_items:
                item_filter = [item_type]
                items = lck.find_all(item_filter, filter_include=False)
                assert len(items) == len(lck.registered_items) - 1
                for it in items:
                    assert it.item_type != item_type
            return

    @pytest.mark.negative
    def test_get_missing_item(self, tmp_path, datadir, setup_and_teardown):
        all_lockers = list(self.lockers.values()) + [self.my_locker]
        for lck in all_lockers:
            with pytest.raises(PhibesNotFoundError):
                lck.get_item("never", "secret")
        return

    @pytest.mark.positive
    def test_update_item(self, setup_and_teardown):
        content = (
            f"here is some stuff"
            f"password: Iwashacked007"
            f"template:my_template"
        )
        all_lockers = list(self.lockers.values()) + [self.my_locker]
        for lck in all_lockers:
            found = lck.get_item("secret_name", "secret")
            assert found
            found.content = content
            lck.update_item(found)
            refound = lck.get_item("secret_name", "secret")
            test_cont = refound.content
            assert test_cont == content


class TestFileNames(EmptyLocker):

    @pytest.mark.positive
    def test_xcode_file_name(self, setup_and_teardown):
        encoded = {}
        all_lockers = copy(self.lockers)
        all_lockers['default'] = self.my_locker
        for lck_name, lck in all_lockers.items():
            for it in lck.registered_items.keys():
                fn = lck.encode_item_name(it, f"{it}_name")
                assert fn.endswith('.cry')
                if 'plain' not in str(type(lck.crypt_impl)):
                    assert it not in fn, f"{lck.crypt_impl}"
                    assert "name" not in fn, f"{lck.crypt_impl}"
                encoded[f"{it}"] = fn
            for it in encoded:
                item_type, item_name = lck.decode_item_name(encoded[it])
                assert item_type in lck.registered_items.keys()
                assert item_name == f"{item_type}_name"


class TestAuth(EmptyLocker):

    @pytest.mark.negative
    def test_fail_auth(self, setup_and_teardown):
        wrong_pw = "ThisWillNotBeIt"
        with pytest.raises(PhibesAuthError):
            self.my_locker = Locker.get(self.locker_name, wrong_pw)

    def custom_setup(self, tmp_path):
        super(TestAuth, self).custom_setup(tmp_path)

    def custom_teardown(self, tmp_path):
        super(TestAuth, self).custom_teardown(tmp_path)
