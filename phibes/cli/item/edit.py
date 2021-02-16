"""
Click command for `edit`
"""

# core library modules
# third party packages
# in-project modules
from phibes.cli.command_base import PhibesCommand
from phibes.cli.command_base import config_option
from phibes.cli.lib import edit_item
from phibes.cli.lib import get_locker_args
from phibes.cli.errors import PhibesCliError
from phibes.cli.options import item_name_option
from phibes.cli.options import locker_name_option, locker_path_option
from phibes.cli.options import password_option


class EditItem(PhibesCommand):
    """
    Class to create and run click command to create and add an item to a locker
    """

    options = {
        'config': config_option,
        'path': locker_path_option,
        'password': password_option,
        'item': item_name_option
    }

    def __init__(self):
        super(EditItem, self).__init__()

    @staticmethod
    def handle(*args, **kwargs) -> None:
        """Create and edit an item in a locker"""
        super(EditItem, EditItem).handle(*args, **kwargs)
        try:
            item_name = kwargs.get('item')
        except KeyError as err:
            raise PhibesCliError(f'missing required param {err}')
        inst = get_locker_args(*args, **kwargs)
        edit_item(locker_inst=inst, item_name=item_name)


class EditItemNamedLocker(EditItem):

    options = {
        'config': config_option,
        'locker': locker_name_option,
        'password': password_option,
        'item': item_name_option
    }
