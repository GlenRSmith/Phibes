"""
pytest module for lib.locker
"""

# Standard library imports
from copy import copy

# Related third party imports
import pytest

# Local application/library specific imports
from phibes import crypto
from phibes.lib.errors import PhibesAuthError
from phibes.lib.errors import PhibesExistsError
from phibes.lib.errors import PhibesNotFoundError
from phibes.model import Locker

# Local test imports
from tests.lib.test_helpers import ConfigLoadingTestClass
from tests.lib.test_helpers import EmptyLocker, plain_texts, PopulatedLocker


crypt_list = crypto.list_crypts()


class TestLocker(EmptyLocker):

    my_locker = None
    locker_name = "my_locker"
    password = "StaplerRadioPersonWomanMan"

    def custom_setup(self, tmp_path):
        super(TestLocker, self).custom_setup(tmp_path)
        try:
            if Locker.get(
                    password=self.password, locker_name=self.locker_name
            ):
                Locker.delete(
                    password=self.password, locker_name=self.locker_name
                )
        except Exception:
            pass

    def custom_teardown(self, tmp_path):
        super(TestLocker, self).custom_teardown(tmp_path)
        try:
            Locker.delete(
                password=self.password, locker_name=self.locker_name
            )
        except PhibesNotFoundError:
            pass

    @pytest.mark.positive
    def test_good(self, tmp_path, datadir, setup_and_teardown):
        Locker.create(
            password=self.password,
            crypt_id=crypto.default_id,
            locker_name=self.locker_name
        )
        found = Locker.get(password=self.password, locker_name=self.locker_name)
        assert found

    @pytest.mark.negative
    def test_duplicate(self, tmp_path, datadir, setup_and_teardown):
        Locker.create(
            password=self.password,
            crypt_id=crypto.default_id,
            locker_name=self.locker_name
        )
        with pytest.raises(PhibesExistsError):
            Locker.create(
                password=self.password,
                crypt_id=crypto.default_id,
                locker_name=self.locker_name
            )


class TestNoName(ConfigLoadingTestClass):

    password = "78CollECtion!CampCoolio"

    @pytest.mark.parametrize("crypt_id", crypt_list)
    @pytest.mark.positive
    def test_create_with_arg(self, crypt_id, setup_and_teardown):
        Locker.create(
            password=self.password, crypt_id=crypt_id, locker_name=None
        )
        found = Locker.get(password=self.password, locker_name=None)
        assert found

    @pytest.mark.parametrize("crypt_id", crypt_list)
    @pytest.mark.positive
    def test_create_without_arg(self, crypt_id, setup_and_teardown):
        Locker.create(password=self.password, crypt_id=crypt_id)
        found = Locker.get(password=self.password, locker_name=None)
        assert found


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
    """
    def get_item_path(self, item_name: str) -> Path:
        file_name = f"{self.encrypt(item_name)}.{FILE_EXT}"
        return self.path.joinpath(file_name)

    """
    @pytest.mark.positive
    def test_xcode_file_name(self, setup_and_teardown):
        encoded = {}
        all_lockers = copy(self.lockers)
        all_lockers['default'] = self.my_locker
        for lck_name, lck in all_lockers.items():
            if 'plain' not in str(type(lck.crypt_impl)):
                assert "secret" not in lck.encrypt("secret_name")
                assert "name" not in lck.encrypt("secret_name")


class TestAuth(EmptyLocker):

    @pytest.mark.negative
    def test_fail_auth(self, setup_and_teardown):
        wrong_pw = "ThisWillNotBeIt"
        with pytest.raises(PhibesAuthError):
            self.my_locker = Locker.get(
                password=wrong_pw, locker_name=self.locker_name
            )

    def custom_setup(self, tmp_path):
        super(TestAuth, self).custom_setup(tmp_path)

    def custom_teardown(self, tmp_path):
        super(TestAuth, self).custom_teardown(tmp_path)
