"""
pytest module for lib.item
"""

# Standard library imports
from datetime import datetime

# Related third party imports
import pytest

# Local application/library specific imports
from phibes.model import Item

# Local test imports
from tests.lib.test_helpers import EmptyLocker, plain_texts


class TestCreate(EmptyLocker):

    @pytest.mark.negative
    def test_create_empty_items(self, setup_and_teardown):
        all_lockers = list(self.lockers.values()) + [self.my_locker]
        for lck in all_lockers:
            pth = lck.get_item_path("secret_name")
            new_item = Item(lck.crypt_impl, "secret_name")
            with pytest.raises(AttributeError):
                new_item.save(pth)


class TestCreateAndSave(EmptyLocker):

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plain_texts)
    def test_create_items(self, plaintext, setup_and_teardown):
        all_lockers = list(self.lockers.values()) + [self.my_locker]
        for lck in all_lockers:
            content = (
                f"{plaintext}"
                f"here is some stuff"
                f"password: HardHat"
                f"secret_name"
            )
            pth = lck.get_item_path("secret_name")
            new_item = Item(lck.crypt_impl, "secret_name")
            new_item.content = content
            new_item.save(pth)
            pth = lck.get_item_path("secret_name")
            found = Item(lck.crypt_impl, "secret_name")
            found.read(pth)
            assert found

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plain_texts)
    def test_create_item(self, plaintext, setup_and_teardown):
        all_lockers = list(self.lockers.values()) + [self.my_locker]
        for lck in all_lockers:
            content = (
                f"{plaintext}"
                f"here is some stuff"
                f"password: HardHat"
                f"template:my_template"
            )
            pth = lck.get_item_path("secret_name")
            new_item = Item(lck.crypt_impl, "sekrit_name")
            new_item.content = content
            new_item.save(pth)
            found = Item(lck.crypt_impl, "sekrit_name")
            found.read(pth)
            assert found

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plain_texts)
    def test_content(self, plaintext, setup_and_teardown):
        all_lockers = list(self.lockers.values()) + [self.my_locker]
        for lck in all_lockers:
            content = f"{plaintext}\ndoes content work?"
            new_item = lck.create_item('any name')
            new_item.content = content
            lck.add_item(new_item)
            found = lck.get_item('any name')
            assert content == found.content, (
                f"{lck.crypt_impl=}" f"{str(found)=}"
            )

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plain_texts)
    def test_fields(self, plaintext, setup_and_teardown):
        all_lockers = list(self.lockers.values()) + [self.my_locker]
        for lck in all_lockers:
            content = f"{plaintext}\ndo all fields work?"
            new_item = lck.create_item('any name')
            new_item.content = content
            lck.add_item(new_item)
            found = lck.get_item('any name')
            test_fields = [
                'salt', 'timestamp', 'content', 'name', '_ciphertext'
            ]
            for fld in test_fields:
                set_val = getattr(new_item, fld)
                found_val = getattr(found, fld)
                assert set_val == found_val, (
                    f"         mismatching saved/retrieved {fld=}       "
                    f"     {set_val=}/{found_val}                       "
                )
            assert content == found.content, (
                f"{lck.crypt_impl=}" f"{str(found)=}"
            )

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plain_texts)
    def test_modified_on_save(self, plaintext, setup_and_teardown):
        all_lockers = list(self.lockers.values()) + [self.my_locker]
        for lck in all_lockers:
            content = f"{plaintext}\ndoes saving update instance?"
            new_item = lck.create_item('any name')
            new_item.content = content
            lck.add_item(new_item)
            found = lck.get_item('any name')
            test_fields = [
                'salt', 'timestamp', 'content', 'name', '_ciphertext'
            ]
            for fld in test_fields:
                assert getattr(new_item, fld) is not None, (
                    f"   {fld=} is None      "
                )
            assert content == found.content, (
                f"{lck.crypt_impl=}" f"{str(found)=}"
            )

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plain_texts)
    def test_timestamp(self, plaintext, setup_and_teardown):
        all_lockers = list(self.lockers.values()) + [self.my_locker]
        for lck in all_lockers:
            content = f"{plaintext}\ndo timestamps work?"
            new_item = lck.create_item('any name')
            new_item.content = content
            lck.add_item(new_item)
            err_msg = (
                f"       {new_item.timestamp}   "
                f"       {dir(new_item)=}   "
                f"       {new_item.as_dict()=}    "
            )
            new_ts = new_item.timestamp
            assert new_ts is not None, err_msg
            assert datetime.strptime(new_ts, '%Y-%m-%d %H:%M:%S.%f'), err_msg
            found = lck.get_item('any name')
            assert new_ts == found.timestamp, f"{lck.crypt_impl=}"
            try:
                datetime.strptime(found.timestamp, '%Y-%m-%d %H:%M:%S.%f')
            except Exception as err:
                pytest.fail(f"invalid datetime str: {new_ts}\n{err}")


class TestItems(EmptyLocker):

    @pytest.mark.positive
    @pytest.mark.parametrize("plaintext", plain_texts)
    def test_string_add_content(self, plaintext, setup_and_teardown):
        # can I += the content field?
        all_lockers = list(self.lockers.values()) + [self.my_locker]
        for lck in all_lockers:
            s1 = lck.create_item("facebook")
            s1.content = "initial content"
            lck.add_item(s1)
            s2 = lck.get_item("facebook")
            assert s2.content == "initial content"
            s2.content += f" - {plaintext}"
            lck.update_item(s2)
            s3 = lck.get_item("facebook")
            assert s3.content == f"initial content - {plaintext}"
