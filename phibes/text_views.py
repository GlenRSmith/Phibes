"""
Phibes operation functions with only primitive-type params
Like HTTP views, but just text for CLI
"""

# core library modules
# third party packages
# in-project modules
from phibes.model import Locker
from phibes.lib.represent import rendered


def create_locker(crypt_id: str, **kwargs):
    pw = kwargs.get('password')
    locker_name = kwargs.get('locker_name', None)
    return Locker.create(
        password=pw, crypt_id=crypt_id, locker_name=locker_name
    )


@rendered
def get_locker(password: str, locker_name: str, **kwargs):
    return Locker.get(password=password, locker_name=locker_name)


def delete_locker(password: str, locker_name: str, **kwargs):
    return Locker.get(
        password=password, locker_name=locker_name
    ).delete_instance()


def create_item(
        password: str,
        locker_name: str,
        item_name: str,
        content: str,
        **kwargs
):
    locker = Locker.get(password=password, locker_name=locker_name)
    item = locker.create_item(item_name=item_name)
    item.content = content
    return locker.add_item(item)


def update_item(
        password: str,
        locker_name: str,
        item_name: str,
        content: str,
        **kwargs
):
    locker = Locker.get(password=password, locker_name=locker_name)
    item = locker.get_item(item_name)
    item.content = content
    return locker.update_item(item)


def get_item(password: str, locker_name: str, item_name: str, **kwargs):
    locker = Locker.get(password=password, locker_name=locker_name)
    return locker.get_item(item_name=item_name)


def get_items(password: str, locker_name: str, **kwargs):
    locker = Locker.get(password=password, locker_name=locker_name)
    return locker.list_items()


def delete_item(
        password: str, locker_name: str, item_name: str, **kwargs
):
    locker = Locker.get(password=password, locker_name=locker_name)
    locker.delete_item(item_name=item_name)
