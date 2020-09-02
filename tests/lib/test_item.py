"""
pytest module for lib.item
"""

# Standard library imports
from datetime import datetime

# Related third party imports
import pytest

# Local application/library specific imports
from phibes.lib.item import Item

# Local test imports
from tests.lib.locker_helper import EmptyLocker


class TestCreate(EmptyLocker):

    @pytest.mark.negative
    def test_create_empty_items(self, setup_and_teardown):
        for item_type in self.my_locker.registered_items.keys():
            pth = self.my_locker.get_item_path(
                f"{item_type}", f"{item_type}_name"
            )
            new_item = Item(
                self.my_locker.crypt_impl,
                f"{item_type}_name"
            )
            with pytest.raises(AttributeError):
                new_item.save(pth)


class TestCreateAndSave(EmptyLocker):

    @pytest.mark.positive
    def test_create_items(self, setup_and_teardown):
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
                self.my_locker.crypt_impl,
                f"{item_type}_name"
            )
            new_item.content = content
            new_item.save(pth)
        for item_type in self.my_locker.registered_items.keys():
            pth = self.my_locker.get_item_path(
                f"{item_type}",
                f"{item_type}_name"
            )
            found = Item(
                self.my_locker.crypt_impl,
                f"{item_type}_name"
            )
            found.read(pth)
            assert found

    @pytest.mark.positive
    def test_create_item(self, setup_and_teardown):
        content = (
            f"here is some stuff"
            f"password: HardHat"
            f"template:my_template"
        )
        pth = self.my_locker.get_item_path(
            f"secret", f"secret_name",
        )
        new_item = Item(
            self.my_locker.crypt_impl,
            f"sekrit_name"
        )
        new_item.content = content
        new_item.save(pth)
        found = Item(
            self.my_locker.crypt_impl,
            f"sekrit_name"
        )
        found.read(pth)
        assert found

    @pytest.mark.positive
    def test_content(self, setup_and_teardown):
        k = self.my_locker
        content = f"does content work?"
        new_item = self.my_locker.create_item('any name', 'secret')
        new_item.content = content
        k.add_item(new_item)
        found = k.get_item('any name', 'secret')
        assert content == found.content

    @pytest.mark.positive
    def test_timestamp(self, setup_and_teardown):
        k = self.my_locker
        content = f"do timestamps work?"
        new_item = self.my_locker.create_item('any name', 'secret')
        new_item.content = content
        k.add_item(new_item)
        new_ts = new_item.timestamp
        try:
            datetime.strptime(new_ts, '%Y-%m-%d %H:%M:%S.%f')
        except Exception as err:
            pytest.fail(f"invalid datetime str: {new_ts}\n{err}")
        found = k.get_item('any name', 'secret')
        assert new_ts == found.timestamp
        try:
            datetime.strptime(found.timestamp, '%Y-%m-%d %H:%M:%S.%f')
        except Exception as err:
            pytest.fail(f"invalid datetime str: {new_ts}\n{err}")


class TestItems(EmptyLocker):

    @pytest.mark.positive
    def test_string_add_content(self, setup_and_teardown):
        # can I += the content field?
        k = self.my_locker
        s1 = k.create_item("facebook", "secret")
        s1.content = "initial content"
        k.add_item(s1)
        s2 = k.get_item("facebook", "secret")
        assert s2.content == "initial content"
        s2.content += " - more content"
        k.update_item(s2)
        s3 = k.get_item("facebook", "secret")
        assert s3.content == "initial content - more content"
