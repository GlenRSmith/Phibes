"""
Phibes operation functions with only primitive-type params
Like HTTP views, but just text for CLI
"""

# core library modules
import json

# third party packages
# in-project modules
from phibes.model import Locker
from phibes.lib.represent import ReprType, rendered
from phibes.lib.utils import todict


def _get_locker_helper(locker_args, update_args=False):
    if update_args:
        arg_op = locker_args.pop
    else:
        arg_op = locker_args.get
    # unused for now
    # store_type = arg_op('store_type')
    inst = Locker.get(
        password=arg_op('password'), name=arg_op('locker', None)
    )
    return inst


def render_response(object, repr: ReprType = ReprType.Object):
    if repr == ReprType.Object:
        return object
    elif repr == ReprType.JSON:
        return todict(object)
    elif repr == ReprType.Text:
        return json.dumps(todict(object))
    elif repr == ReprType.HTML:
        raise ValueError(f'{repr} not implemented')


def create_locker(crypt_id: str, **kwargs):
    pw = kwargs.get('password')
    name = kwargs.get('locker', None)
    return Locker.create(password=pw, crypt_id=crypt_id, name=name)


@rendered
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
