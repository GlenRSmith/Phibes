"""
pytest module for view:get_locker
"""

# Standard library imports

# Related third party imports
import pytest

# Local application/library specific imports
from phibes import crypto
from phibes.lib.config import ConfigModel
from phibes.lib.errors import PhibesNotFoundError
from phibes.lib.represent import ReprType
from phibes.model import Locker
from phibes.lib import views
from phibes.storage.types import StoreType
from phibes.lib.views import get_locker

# Local test imports
from tests.lib.test_helpers import ConfigLoadingTestClass
from tests.lib.test_helpers import EmptyLocker


class TestGetLocker(EmptyLocker):
    """
    Test the get_locker view function
    """

    my_locker = None
    locker_name = "my_locker"
    password = "StaplerRadioPersonWomanMan"

    def custom_setup(self, tmp_path):
        ConfigModel().storage = StoreType.Memory.name
        super(TestGetLocker, self).custom_setup(tmp_path)
        try:
            if Locker.get(password=self.password, locker_name=self.locker_name):
                Locker.delete(password=self.password, locker_name=self.locker_name)
                Locker.create(
                    password=self.password,
                    crypt_id=crypto.default_id,
                    locker_name=self.locker_name
                )
        except Exception:
            pass

    def custom_teardown(self, tmp_path):
        super(TestGetLocker, self).custom_teardown(tmp_path)
        try:
            Locker.delete(password=self.password, locker_name=self.locker_name)
        except PhibesNotFoundError:
            pass

    @pytest.mark.positive
    def test_get_locker(self, tmp_path, datadir, setup_and_teardown):
        inst = get_locker(
            password=self.password, locker_name=self.locker_name
        )
        assert inst
        assert type(inst) is Locker
        inst = get_locker(
            repr=ReprType.Object,
            password=self.password,
            locker_name=self.locker_name
        )
        assert inst
        assert type(inst) is Locker
        inst = get_locker(
            repr=ReprType.JSON,
            password=self.password,
            locker_name=self.locker_name
        )
        assert inst
        assert type(inst) is dict
        inst = get_locker(
            repr=ReprType.Text,
            password=self.password,
            locker_name=self.locker_name
        )
        assert inst
        assert type(inst) is str


class TestJson(ConfigLoadingTestClass):
    """
    Test a whole lifecycle of lockers,
    including all view functions, relying on "server-side" handling
    of encryption operations.
    In this context, , it is acceptable for the views to return objects
    (rather than JSON and primitives, as in the browser demo).
    """

    repr = ReprType.JSON
    mock_users = {
        'ronald': {'pw': 'curruptFM'},
        'foo': {'pw': 'blah'},
        'shelly': {'pw': '0ntheBeach'}
    }

    def custom_setup(self, tmp_path):
        super(TestJson, self).custom_setup(tmp_path)
        ConfigModel().storage = StoreType.Memory.name

    def custom_teardown(self, tmp_path):
        super(TestJson, self).custom_teardown(tmp_path)

    @pytest.mark.positive
    def test_repr(self, tmp_path, datadir, setup_and_teardown):
        # print('create a locker for each test user:')
        for user, rec in self.mock_users.items():
            locker = views.create_locker(
                password=rec['pw'],
                locker_name=user,
                crypt_id=crypto.default_id,
                repr=self.repr
            )
            assert type(locker) is dict

        # print('get each locker:')
        for user, rec in self.mock_users.items():
            locker = views.get_locker(
                password=rec['pw'], locker_name=user, repr=self.repr
            )
            assert type(locker) is dict

        # print('add an item to the locker for each user')
        for user, rec in self.mock_users.items():
            item_name = 'greeting'
            item_content = f'Hello! My name is {user}'
            item = views.create_item(
                password=self.mock_users[user]['pw'],
                locker_name=user, item_name=item_name,
                content=item_content,
                repr=self.repr
            )
            assert type(item) is dict

        # print('retrieve the lockers and items:')
        for user, rec in self.mock_users.items():
            item_name = 'greeting'
            locker = views.get_locker(
                password=rec['pw'], locker_name=user, repr=self.repr
            )
            assert type(locker) is dict
            item = views.get_item(
                password=self.mock_users[user]['pw'],
                locker_name=user, item_name=item_name,
                repr=self.repr
            )
            assert type(item) is dict

        # print('update the items:')
        for user, rec in self.mock_users.items():
            item_name = 'greeting'
            locker = views.get_locker(
                password=rec['pw'], locker_name=user,
                repr=self.repr
            )
            assert type(locker) is dict
            item = views.update_item(
                password=self.mock_users[user]['pw'],
                locker_name=user, item_name=item_name,
                content=f'Goodbye! My name is {user}',
                repr=self.repr,
            )
            assert type(item) is dict

        # print('retrieve the lockers and items:')
        for user, rec in self.mock_users.items():
            item_name = 'greeting'
            locker = views.get_locker(
                password=rec['pw'], locker_name=user, repr=self.repr
            )
            assert type(locker) is dict
            item = views.get_item(
                password=self.mock_users[user]['pw'],
                locker_name=user, item_name=item_name,
                repr=self.repr
            )
            assert type(item) is dict

        # print('retrieve the lockers and item lists:')
        for user, rec in self.mock_users.items():
            locker = views.get_locker(
                repr=self.repr, password=rec['pw'], locker_name=user
            )
            assert type(locker) is dict
            items = views.get_items(
                repr=self.repr,
                password=self.mock_users[user]['pw'],
                locker_name=user
            )
            assert type(items) is list
            for item in items:
                assert type(item) is dict

        # print('delete items:')
        for user, rec in self.mock_users.items():
            item_name = 'greeting'
            locker = views.get_locker(
                repr=self.repr, password=rec['pw'], locker_name=user
            )
            assert type(locker) is dict
            # print(f'{locker.__dict__=}')
            views.delete_item(
                repr=self.repr,
                password=self.mock_users[user]['pw'],
                locker_name=user, item_name=item_name
            )

        # print('delete lockers:')
        for user, rec in self.mock_users.items():
            views.delete_locker(
                repr=self.repr, password=rec['pw'], locker_name=user
            )
