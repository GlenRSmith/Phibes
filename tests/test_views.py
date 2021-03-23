"""
pytest module for testing views
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
from phibes import text_views
from phibes.storage.types import StoreType
from phibes.text_views import get_locker

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


class TestDemoTextViews(ConfigLoadingTestClass):
    """
    Test a whole lifecycle of lockers
    """

    mock_users = {
        'ronald': {'pw': 'curruptFM'},
        'foo': {'pw': 'blah'},
        'shelly': {'pw': '0ntheBeach'}
    }

    def custom_setup(self, tmp_path):
        super(TestDemoTextViews, self).custom_setup(tmp_path)
        ConfigModel().storage = StoreType.Memory.name

    def custom_teardown(self, tmp_path):
        super(TestDemoTextViews, self).custom_teardown(tmp_path)

    @pytest.mark.positive
    def test_json_repr(self, tmp_path, datadir, setup_and_teardown):
        # print('create a locker for each test user:')
        for user, rec in self.mock_users.items():
            text_views.create_locker(
                password=rec['pw'],
                locker_name=user,
                crypt_id=crypto.default_id
            )

        # print('get each locker:')
        for user, rec in self.mock_users.items():
            text_views.get_locker(password=rec['pw'], locker_name=user)

        # print('add an item to the locker for each user')
        for user, rec in self.mock_users.items():
            item_name = 'greeting'
            item_content = f'Hello! My name is {user}'
            text_views.create_item(
                repr=ReprType.Object,
                password=self.mock_users[user]['pw'],
                locker_name=user, item_name=item_name,
                content=item_content
            )

        # print('retrieve the lockers and items:')
        for user, rec in self.mock_users.items():
            item_name = 'greeting'
            locker = text_views.get_locker(
                repr=ReprType.Object, password=rec['pw'], locker_name=user
            )
            # print(f'{locker.__dict__=}')
            item = text_views.get_item(
                repr=ReprType.Object,
                password=self.mock_users[user]['pw'],
                locker_name=user, item_name=item_name
            )
            # print(f'{item=}')

        # print('update the items:')
        for user, rec in self.mock_users.items():
            item_name = 'greeting'
            locker = text_views.get_locker(
                repr=ReprType.Object,
                password=rec['pw'], locker_name=user
            )
            # print(f'{locker.__dict__=}')
            item = text_views.update_item(
                repr=ReprType.Object,
                password=self.mock_users[user]['pw'],
                locker_name=user, item_name=item_name,
                content=f'Goodbye! My name is {user}'
            )
            # print(f'{item=}')

        # print('retrieve the lockers and items:')
        for user, rec in self.mock_users.items():
            item_name = 'greeting'
            locker = text_views.get_locker(
                repr=ReprType.Object,
                password=rec['pw'], locker_name=user
            )
            # print(f'{locker.__dict__=}')
            item = text_views.get_item(
                repr=ReprType.Object,
                password=self.mock_users[user]['pw'],
                locker_name=user, item_name=item_name
            )
            # print(f'{item=}')

        # print('retrieve the lockers and item lists:')
        for user, rec in self.mock_users.items():
            locker = text_views.get_locker(
                repr=ReprType.Object, password=rec['pw'], locker_name=user
            )
            # print(f'{locker.__dict__=}')
            item = text_views.get_items(
                repr=ReprType.Object,
                password=self.mock_users[user]['pw'],
                locker_name=user
            )
            # print(f'{item=}')

        # print('delete items:')
        for user, rec in self.mock_users.items():
            item_name = 'greeting'
            locker = text_views.get_locker(
                repr=ReprType.Object, password=rec['pw'], locker_name=user
            )
            # print(f'{locker.__dict__=}')
            text_views.delete_item(
                repr=ReprType.Object,
                password=self.mock_users[user]['pw'],
                locker_name=user, item_name=item_name
            )

        # print('delete lockers:')
        for user, rec in self.mock_users.items():
            text_views.delete_locker(
                repr=ReprType.Object, password=rec['pw'], locker_name=user
            )
