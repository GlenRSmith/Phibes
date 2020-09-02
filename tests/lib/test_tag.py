"""
pytest module for lib.tag
"""

# Standard library imports

# Related third party imports
import pytest

# Local application/library specific imports
from phibes.lib.tag import Tag

# Local test imports
from tests.lib.locker_helper import EmptyLocker


class TestTags(EmptyLocker):

    @pytest.mark.positive
    def test_tags(self, setup_and_teardown):
        # create some secrets
        s1 = self.my_locker.create_item("facebook", "secret")
        s2 = self.my_locker.create_item("twitter", "secret")
        s3 = self.my_locker.create_item("reddit", "secret")
        # create a tag
        t1 = self.my_locker.create_item("social_media", "tag")
        assert t1.list_items() == list()
        # add the secrets to the tag
        # TODO: decide whether unsaved items should be allowed.
        # (these items don't even have assigned content yet!)
        t1.add_item(s1)
        t1.add_item(s2)
        t1.add_item(s3)
        # save the tag
        pth = self.my_locker.get_item_path("tag", "social_media")
        self.my_locker.add_item(t1)
        # list the secrets in the item
        assert "secret:facebook" in t1.content
        assert "secret:twitter" in t1.content
        assert "secret:reddit" in t1.content
        before_len = len(t1.list_items())
        t1.remove_item(s1)
        after_len = len(t1.list_items())
        assert after_len == before_len - 1
        assert "secret:facebook" not in t1.content
        them_secrets = t1.list_items()
        assert sorted(them_secrets) == sorted(
            ["secret:twitter", "secret:reddit"]
        )
        t1.save(pth, overwrite=True)
        t2 = Tag(self.my_locker.crypt_impl, f"social_media")
        t2.read(pth)
        assert t2 is not None
        those_secrets = t2.list_items()
        assert "secret:facebook" not in those_secrets
        assert "secret:twitter" in those_secrets
        assert "secret:reddit" in those_secrets
