"""
Click interface to delete Items
"""

# core library modules
# third party packages
# in-project modules
from phibes.cli.command_base import config_option
from phibes.cli.command_base import PhibesCommand
from phibes.cli.errors import PhibesCliError
from phibes.cli.lib import get_locker_args
from phibes.cli.options import item_name_option
from phibes.cli.options import locker_name_option
from phibes.cli.options import locker_path_option
from phibes.cli.options import password_option


class DeleteItem(PhibesCommand):
    """
    Command to delete an item from a locker
    """

    options = {
        'config': config_option,
        'password': password_option,
        'path': locker_path_option,
        'item': item_name_option
    }

    def __init__(self):
        super(DeleteItem, self).__init__()

    @staticmethod
    def handle(*args, **kwargs):
        """
        Delete an item from the locker
        """
        super(DeleteItem, DeleteItem).handle(*args, **kwargs)
        try:
            item_name = kwargs.get('item')
            if not item_name:
                raise KeyError('item')
        except KeyError as err:
            raise PhibesCliError(f'missing required param {err}')
        inst = get_locker_args(*args, **kwargs)
        inst.delete_item(item_name)


class DeleteItemNamedLocker(DeleteItem):
    """
    Class to create & run click command to delete an item from a named locker
    """

    options = {
        'config': config_option,
        'password': password_option,
        'locker': locker_name_option,
        'item': item_name_option
    }
