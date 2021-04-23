"""
Phibes operation functions that are decorated to allow return type
to be specified by caller (e.g. JSON, Object, Text, HTML)
Hence, provides a common entry point for various client types.
"""

# core library modules
# third party packages
# in-project modules
from phibes.model import Locker


def create_locker(
        password: str,
        crypt_id: str,
        locker_name: str = None,
        **kwargs
):
    return Locker.create(
        password=password, crypt_id=crypt_id, locker_name=locker_name
    ).to_dict()


def get_locker(password: str, locker_name: str, **kwargs):
    return Locker.get(password=password, locker_name=locker_name).to_dict()


def delete_locker(password: str, locker_name: str, **kwargs):
    return Locker.delete(password=password, locker_name=locker_name)


def create_item(
        password: str, locker_name: str, item_name: str, content: str, **kwargs
):
    locker = Locker.get(password=password, locker_name=locker_name)
    item = locker.create_item(item_name=item_name)
    item.content = content
    locker.add_item(item)
    return get_item(
        password=password, locker_name=locker_name, item_name=item_name
    )


def update_item(
        password: str, locker_name: str, item_name: str, content: str, **kwargs
):
    locker = Locker.get(password=password, locker_name=locker_name)
    item = locker.get_item(item_name)
    item.content = content
    locker.update_item(item)
    return get_item(
        password=password, locker_name=locker_name, item_name=item_name
    )


def get_item(password: str, locker_name: str, item_name: str, **kwargs):
    locker = Locker.get(password=password, locker_name=locker_name)
    return locker.get_item(item_name=item_name).as_dict()


def get_items(password: str, locker_name: str, **kwargs):
    locker = Locker.get(password=password, locker_name=locker_name)
    return [item.as_dict() for item in locker.list_items()]


def delete_item(
        password: str, locker_name: str, item_name: str, **kwargs
):
    locker = Locker.get(password=password, locker_name=locker_name)
    return locker.delete_item(item_name=item_name)
