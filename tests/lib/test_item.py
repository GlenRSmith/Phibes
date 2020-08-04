"""
pytest module for lib.item
"""

# Standard library imports

# Related third party imports

# Local application/library specific imports
from privacy_playground.lib.item import Item
from locker_helper import LockerHelper


class TestCreate(LockerHelper):

    def test_create_empty_items(self):
        for item_type in Item.get_item_types():
            new_item = Item(
                self.my_locker,
                f"{item_type}_name",
                f"{item_type}",
                create=True
            )


class TestCreateAndSave(LockerHelper):

    def test_create_items(self):
        for item_type in Item.get_item_types():
            content = (
                f"here is some stuff"
                f"password: HardHat"
                f"{item_type}:{item_type}_name"
            )
            new_item = Item(
                TestCreate.my_locker,
                f"{item_type}_name",
                f"{item_type}",
                create=True
            )
            new_item.content = content
            new_item.save()
        for item_type in Item.get_item_types():
            found = Item(
                TestCreateAndSave.my_locker,
                f"{item_type}_name",
                f"{item_type}"
            )
            assert found

    def test_create_item(self):
        content = (
            f"here is some stuff"
            f"password: HardHat"
            f"template:my_template"
        )
        new_item = Item(
            TestCreate.my_locker,
            f"sekrit_name",
            f"secret",
            create=True
        )
        new_item.content = content
        new_item.save()
        found = Item(
            TestCreateAndSave.my_locker,
            f"sekrit_name",
            f"secret"
        )
        assert found


class TestItems(LockerHelper):

    def test_delete(self):
        pass

    def test_find(self):
        pass

    def test_find_all(self):
        pass

    def test_Xcode_file_name(self):
        encoded = {}
        for it in Item.get_item_types():
            fn = Item.encode_file_name(
                LockerHelper.my_locker, it, f"{it}_name"
            )
            assert fn.name.endswith('.cry')
            assert it not in fn.name
            assert "name" not in fn.name
            encoded[f"{it}"] = fn
        for it in encoded:
            item_type, item_name = Item.decode_file_name(
                LockerHelper.my_locker, encoded[it].name
            )
            assert item_type in Item.get_item_types()
            assert item_name == f"{item_type}_name"

    def test_content(self):
        pass

    def test_timestamp(self):
        pass

    def test_save(self):
        pass


class TestItemTypes(object):

    def test_get_item_types(self):
        item_types = Item.get_item_types()
        assert type(item_types) is list
