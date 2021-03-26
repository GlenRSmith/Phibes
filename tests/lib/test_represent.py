"""
pytest module for lib.represent
"""

# Standard library imports
from copy import deepcopy

# Related third party imports
import pytest

# Local application/library specific imports
from phibes.lib import represent
from phibes.lib.represent import find_conversion
from phibes.lib.represent import render, rendered
from phibes.lib.represent import ReprType

# Local test imports


class FakeItem(object):
    name = 'fake'

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@rendered
def get_fake_item(**kwargs):
    return FakeItem(**kwargs)


class TestConversions(object):

    def setup_method(self):
        represent.path_cache = deepcopy(represent.ConversionMap)

    def teardown_method(self):
        represent.path_cache = deepcopy(represent.ConversionMap)

    @pytest.mark.positive
    def test_find_conversion(self):
        assert ReprType.Object in represent.path_cache
        assert ReprType.JSON in represent.path_cache
        assert ReprType.Text in represent.path_cache
        assert ReprType.HTML not in represent.path_cache
        assert ReprType.JSON in represent.path_cache[ReprType.Object]
        assert ReprType.Text not in represent.path_cache[ReprType.Object]
        assert ReprType.HTML not in represent.path_cache[ReprType.Object]
        assert ReprType.Text in represent.path_cache[ReprType.JSON]
        assert ReprType.Object not in represent.path_cache[ReprType.JSON]
        assert ReprType.HTML not in represent.path_cache[ReprType.JSON]
        assert ReprType.HTML in represent.path_cache[ReprType.Text]
        assert ReprType.Object not in represent.path_cache[ReprType.Text]
        assert ReprType.JSON not in represent.path_cache[ReprType.Text]
        find_conversion(
            from_type=ReprType.Object, to_type=ReprType.JSON
        )
        find_conversion(
            from_type=ReprType.Object, to_type=ReprType.Text
        )
        assert ReprType.Text in represent.path_cache[ReprType.Object]
        find_conversion(
            from_type=ReprType.Object, to_type=ReprType.HTML
        )
        assert ReprType.HTML in represent.path_cache[ReprType.Object]
        assert ReprType.HTML in represent.path_cache[ReprType.JSON]

    @pytest.mark.positive
    def test_render(self):
        assert ReprType.Object in represent.path_cache
        assert ReprType.JSON in represent.path_cache
        assert ReprType.Text in represent.path_cache
        assert ReprType.HTML not in represent.path_cache
        assert ReprType.JSON in represent.path_cache[ReprType.Object]
        assert ReprType.Text not in represent.path_cache[ReprType.Object]
        assert ReprType.HTML not in represent.path_cache[ReprType.Object]
        assert ReprType.Text in represent.path_cache[ReprType.JSON]
        assert ReprType.Object not in represent.path_cache[ReprType.JSON]
        assert ReprType.HTML not in represent.path_cache[ReprType.JSON]
        assert ReprType.HTML in represent.path_cache[ReprType.Text]
        assert ReprType.Object not in represent.path_cache[ReprType.Text]
        assert ReprType.JSON not in represent.path_cache[ReprType.Text]
        fake_item = FakeItem()
        fake_item_dict = render(
            origin=fake_item, from_type=ReprType.Object, to_type=ReprType.JSON
        )
        assert type(fake_item_dict) is dict
        fake_item_str = render(
            origin=fake_item, from_type=ReprType.Object, to_type=ReprType.Text
        )
        assert type(fake_item_str) is str
        assert ReprType.Text in represent.path_cache[ReprType.Object]
        fake_item_html = render(
            origin=fake_item, from_type=ReprType.Object, to_type=ReprType.HTML
        )
        assert type(fake_item_html) is str
        assert ReprType.HTML in represent.path_cache[ReprType.Object]
        assert ReprType.HTML in represent.path_cache[ReprType.JSON]

    @pytest.mark.positive
    def test_decorator(self):
        fake_item = get_fake_item(name='here test this')
        assert type(get_fake_item()) is FakeItem
        assert hasattr(fake_item, 'name')
        assert getattr(fake_item, 'name') == 'here test this'
        fake_item = get_fake_item(
            repr=ReprType.Object, name='be more explicit'
        )
        assert type(get_fake_item()) is FakeItem
        assert hasattr(fake_item, 'name')
        assert getattr(fake_item, 'name') == 'be more explicit'
        fake_item = get_fake_item(
            repr=ReprType.JSON, name='make it a dict'
        )
        assert type(fake_item) is dict
        assert fake_item['name'] == 'make it a dict'
        fake_item = get_fake_item(
            repr=ReprType.Text, name='make it a string'
        )
        assert type(fake_item) is str
        assert 'make it a string' in fake_item



