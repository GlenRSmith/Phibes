"""
pytest module for lib.tag
"""

# Standard library imports

# Related third party imports

# Local application/library specific imports
# from privacy_playground.lib.item import Item
from privacy_playground.lib.secret import Secret
from privacy_playground.lib.tag import Tag
from locker_helper import LockerHelper


class TestTags(LockerHelper):

    def test_tags(self):
        # create some secrets
        s1 = Secret(TestTags.my_locker, "facebook", create=True)
        s2 = Secret(TestTags.my_locker, "twitter", create=True)
        s3 = Secret(TestTags.my_locker, "reddit", create=True)
        # create a tag
        t1 = Tag(TestTags.my_locker, "social_media", create=True)
        assert t1.list_items() == list()
        # add the secrets to the tag
        t1.add_item(s1)
        t1.add_item(s2)
        t1.add_item(s3)
        # save the tag
        t1.save()
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
        t1.save(overwrite=True)
        t2 = Tag.find(TestTags.my_locker, "social_media", "tag")
        assert t2 is not None
        assert "secret:facebook" not in t2.content
        assert "secret:twitter" in t2.content
        assert "secret:reddit" in t2.content
