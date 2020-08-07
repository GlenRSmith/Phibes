"""
pytest module for lib.template
"""

# Standard library imports
import json

# Related third party imports

# Local application/library specific imports
# from privacy_playground.lib.locker import Locker
# from privacy_playground.lib.item import Item
from privacy_playground.lib.secret import Secret
from privacy_playground.lib.template import Template
from locker_helper import EmptyLocker


class TestTemplate(EmptyLocker):

    def test_template(self):
        # create a template
        t1 = self.my_locker.create_item("basic", "template")
        form = {
            "username": "",
            "password": ""
        }
        t1.content = json.dumps(form)
        self.my_locker.add_item(t1)
        # create a secrets
        s1 = self.my_locker.create_item(
            item_name="facebook",
            item_type="secret",
            template_name="basic"
        )
        assert s1 is not None
        assert s1.content == json.dumps(form)