"""
pytest module for lib.locker
"""

# Standard library imports

# Related third party imports
import pytest

# Local application/library specific imports
from phibes.lib.locker import Locker

# Local test imports
# from tests.cli.click_test_helpers import update_config_option_default
from tests.lib.locker_helper import EmptyLocker, PopulatedLocker
from tests.lib.locker_helper import setup_and_teardown


class TestLocker(EmptyLocker):

    my_locker = None
    locker_name = "my_locker"
    password = "StaplerRadioPersonWomanMan"

    def custom_setup(self, tmp_path):
        super(TestLocker, self).custom_setup(tmp_path)
        try:
            if Locker(self.locker_name, self.password):
                Locker.delete(self.locker_name, self.password)
        except:
            pass

    def custom_teardown(self, tmp_path):
        super(TestLocker, self).custom_teardown(tmp_path)
        try:
            Locker.delete(self.locker_name, self.password)
        except FileNotFoundError:
            pass

    def test_good(self, tmp_path, datadir, setup_and_teardown):
        Locker(self.locker_name, self.password, create=True)
        found = Locker(
            self.locker_name, self.password, create=False
        )
        assert found
        return


class TestItemStuff(PopulatedLocker):

    def test_find_all(self, tmp_path, datadir, setup_and_teardown):
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

    def test_get_missing_item(self, tmp_path, datadir, setup_and_teardown):
        with pytest.raises(FileNotFoundError):
            self.my_locker.get_item("never", "secret")
        return

    def test_update_item(self, setup_and_teardown):
        content = (
            f"here is some stuff"
            f"password: Iwashacked007"
            f"template:my_template"
        )
        found = self.my_locker.get_item("secret_name", "secret")
        assert found
        found.content = content
        self.my_locker.update_item(found)
        refound = self.my_locker.get_item("secret_name", "secret")
        test_cont = refound.content
        assert test_cont == content


class TestFileNames(EmptyLocker):

    def test_xcode_file_name(self, setup_and_teardown):
        encoded = {}
        for it in self.my_locker.registered_items.keys():
            fn = self.my_locker.encode_item_name(it, f"{it}_name")
            assert fn.endswith('.cry')
            assert it not in fn
            assert "name" not in fn
            encoded[f"{it}"] = fn
        for it in encoded:
            item_type, item_name = self.my_locker.decode_item_name(
                encoded[it]
            )
            assert item_type in self.my_locker.registered_items.keys()
            assert item_name == f"{item_type}_name"


class TestAuth(EmptyLocker):

    @pytest.mark.negative
    def test_fail_auth(self, setup_and_teardown):
        wrong_pw = "ThisWillNotBeIt"
        with pytest.raises(ValueError):
            self.my_locker = Locker(
                self.locker_name, wrong_pw, create=False
            )

    def custom_setup(self, tmp_path):
        super(TestAuth, self).custom_setup(tmp_path)

    def custom_teardown(self, tmp_path):
        super(TestAuth, self).custom_teardown(tmp_path)

