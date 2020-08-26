"""
shared pytest fixtures
"""

# core library

# third party
import pytest

# in project


@pytest.fixture
def setup_and_teardown(request, tmp_path):
    """
    Injecting this fixture into a test method causes that method to
    use `custom_setup` and `custom_teardown` for setup and teardown.

    This allows the tmp_path fixture to be used in setup and teardown.
    """
    if hasattr(request.instance, 'custom_setup'):
        if callable(getattr(request.instance, 'custom_setup')):
            request.instance.custom_setup(tmp_path)
    yield
    if hasattr(request.instance, 'custom_teardown'):
        if callable(getattr(request.instance, 'custom_teardown')):
            request.instance.custom_teardown(tmp_path)
