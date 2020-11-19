"""
pytest module for lib.locker
"""

# Standard library imports
from copy import copy

# Related third party imports
import pytest

# Local application/library specific imports
from phibes.lib.errors import PhibesAuthError
from phibes.lib.errors import PhibesExistsError
from phibes.lib.errors import PhibesNotFoundError
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

    @pytest.mark.negative
    def test_duplicate(self, tmp_path, datadir, setup_and_teardown):
        Locker.create(self.locker_name, self.password)
        with pytest.raises(PhibesExistsError):
            Locker.create(self.locker_name, self.password)


class TestItemStuff(PopulatedLocker):

    @pytest.mark.positive
    def test_find_all(self, tmp_path, datadir, setup_and_teardown):
        all_lockers = list(self.lockers.values()) + [self.my_locker]
        for lck in all_lockers:
            all = lck.list_items()
            assert all != []
            assert len(all) == 1
            return

    @pytest.mark.negative
    def test_get_missing_item(self, tmp_path, datadir, setup_and_teardown):
        all_lockers = list(self.lockers.values()) + [self.my_locker]
        for lck in all_lockers:
            with pytest.raises(PhibesNotFoundError):
                lck.get_item("never")
        return

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plain_texts)
    def test_update_item(self, plaintext, setup_and_teardown):
        all_lockers = list(self.lockers.values()) + [self.my_locker]
        for lck in all_lockers:
            found = lck.get_item("secret_name")
            assert found
            found.content = plaintext
            lck.update_item(found)
            refound = lck.get_item("secret_name")
            assert refound.content == plaintext


class TestFileNames(EmptyLocker):

    @pytest.mark.positive
    def test_xcode_file_name(self, setup_and_teardown):
        encoded = {}
        all_lockers = copy(self.lockers)
        all_lockers['default'] = self.my_locker
        for lck_name, lck in all_lockers.items():
            fn = lck.encode_item_name("secret_name")
            assert fn.endswith('.cry')
            if 'plain' not in str(type(lck.crypt_impl)):
                assert "secret" not in fn, f"{lck.crypt_impl}"
                assert "name" not in fn, f"{lck.crypt_impl}"
            encoded["secret"] = fn
            for it in encoded:
                item_name = lck.decode_item_name(encoded[it])
                assert item_name == f"secret_name"


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
