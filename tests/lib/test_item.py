"""
pytest module for lib.item
"""

# Standard library imports

# Related third party imports
import pytest

# Local application/library specific imports
from privacy_playground.lib.item import Item
from locker_helper import EmptyLocker


class TestCreate(EmptyLocker):

    def test_create_empty_items(self):
        for item_type in self.my_locker.registered_items.keys():
            pth = self.my_locker.get_item_path(
                f"{item_type}", f"{item_type}_name"
            )
            new_item = Item(
                self.my_locker.crypt_key,
                f"{item_type}_name"
            )
            with pytest.raises(AttributeError):
                new_item.save(pth)


class TestCreateAndSave(EmptyLocker):

    def test_create_items(self):
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
                self.my_locker.crypt_key,
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
                self.my_locker.crypt_key,
                f"{item_type}_name"
            )
            found.read(pth)
            assert found

    def test_create_item(self):
        content = (
            f"here is some stuff"
            f"password: HardHat"
            f"template:my_template"
        )
        pth = self.my_locker.get_item_path(
            f"secret", f"secret_name",
        )
        new_item = Item(
            self.my_locker.crypt_key,
            f"sekrit_name"
        )
        new_item.content = content
        new_item.save(pth)
        found = Item(
            self.my_locker.crypt_key,
            f"sekrit_name"
        )
        found.read(pth)
        assert found


class TestItems(EmptyLocker):

    def test_string_add_content(self):
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

    def test_Xcode_file_name(self):
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

    def _test_content(self):
        pass

    def _test_timestamp(self):
        pass
