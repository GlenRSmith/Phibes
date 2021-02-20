"""
Phibes operation functions with only primitive-type params
Like HTTP views, but just text for CLI
"""

# core library modules
# third party packages
# in-project modules
# from phibes.model import Item
from phibes.model import Locker


def _get_locker_helper(locker_args, update_args=False):
    if update_args:
        arg_op = locker_args.pop
    else:
        arg_op = locker_args.get
    # unused for now
    # store_type = arg_op('store_type')
    return Locker.get(
        password=arg_op('password'),
        name=arg_op('locker', None),
        path=arg_op('store_path')
    )


def create_locker(crypt_id: str, **kwargs):
    pw = kwargs.get('password')
    name = kwargs.get('locker', None)
    pth = kwargs.get('store_path')
    return Locker.create(
        password=pw, crypt_id=crypt_id, name=name, path=pth
    )


def get_locker(**kwargs):
    return _get_locker_helper(locker_args=kwargs)


def delete_locker(**kwargs):
    inst = _get_locker_helper(locker_args=kwargs)
    inst.delete_instance()


def create_item(item_name: str, content: str, **kwargs):
    locker = _get_locker_helper(locker_args=kwargs)
    item = locker.create_item(item_name=item_name)
    item.content = content
    return locker.add_item(item)


def update_item(item_name: str, content: str, **kwargs):
    locker = _get_locker_helper(locker_args=kwargs)
    item = locker.get_item(item_name)
    item.content = content
    return locker.update_item(item)


def get_item(item_name: str, **kwargs):
    locker = _get_locker_helper(locker_args=kwargs)
    return locker.get_item(item_name=item_name)


def get_items(**kwargs):
    locker = _get_locker_helper(locker_args=kwargs)
    return locker.list_items()


def delete_item(item_name: str, **kwargs):
    locker = _get_locker_helper(locker_args=kwargs)
    locker.delete_item(item_name=item_name)
