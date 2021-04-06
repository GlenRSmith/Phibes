"""
Phibes operation functions that are decorated to allow return type
to be specified by caller (e.g. JSON, Object, Text, HTML)
Hence, provides a common entry point for various client types.
"""

# core library modules
# third party packages
# in-project modules
from phibes.model import Locker
from phibes.lib.represent import rendered


@rendered
def create_locker(
        password: str,
        crypt_id: str,
        locker_name: str = None,
        **kwargs
):
    return Locker.create(
        password=password, crypt_id=crypt_id, locker_name=locker_name
    )


@rendered
def get_locker(password: str, locker_name: str, **kwargs):
    return Locker.get(password=password, locker_name=locker_name)


@rendered
def delete_locker(password: str, locker_name: str, **kwargs):
    return Locker.delete(password=password, locker_name=locker_name)


@rendered
def create_item(
        password: str, locker_name: str, item_name: str, content: str, **kwargs
):
    locker = Locker.get(password=password, locker_name=locker_name)
    item = locker.create_item(item_name=item_name)
    item.content = content
    return locker.add_item(item)


@rendered
def update_item(
        password: str, locker_name: str, item_name: str, content: str, **kwargs
):
    locker = Locker.get(password=password, locker_name=locker_name)
    item = locker.get_item(item_name)
    item.content = content
    return locker.update_item(item)


@rendered
def get_item(password: str, locker_name: str, item_name: str, **kwargs):
    locker = Locker.get(password=password, locker_name=locker_name)
    return locker.get_item(item_name=item_name)


@rendered
def get_items(password: str, locker_name: str, **kwargs):
    locker = Locker.get(password=password, locker_name=locker_name)
    return locker.list_items()


@rendered
def delete_item(
        password: str, locker_name: str, item_name: str, **kwargs
):
    locker = Locker.get(password=password, locker_name=locker_name)
    return locker.delete_item(item_name=item_name)
