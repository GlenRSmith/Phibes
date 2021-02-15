"""
Click interface to phibes items
"""

# core library modules
# third party packages
import click

# in-project modules
from phibes.cli.lib import present_list_items
from phibes.cli.command_base import config_option
from phibes.cli.command_base import PhibesCommandBareBase
from phibes.cli.lib import get_locker_args
from phibes.cli.options import locker_name_option
from phibes.cli.options import locker_path_option
from phibes.cli.options import password_option
from phibes.cli.options import verbose_item_option


class ListItemsCommand(PhibesCommandBareBase):
    """
    Command to list items in a locker
    """

    options = {
        'config': config_option,
        'password': password_option,
        'path': locker_path_option,
        'verbose': verbose_item_option
    }

    def __init__(self):
        super(ListItemsCommand, self).__init__()

    @staticmethod
    def handle(*args, **kwargs):
        """
        Get an item from the locker
        """
        super(ListItemsCommand, ListItemsCommand).handle(*args, **kwargs)
        verbose = kwargs.get('verbose', False)
        locker_inst = get_locker_args(*args, **kwargs)
        click.echo(present_list_items(locker_inst, verbose))


class ListItemsNamedLockerCmd(ListItemsCommand):
    """
    Class to create & run click command to list items in a named locker
    """

    options = {
        'config': config_option,
        'password': password_option,
        'locker': locker_name_option,
        'verbose': verbose_item_option
    }

    def __init__(self):
        super(ListItemsNamedLockerCmd, self).__init__()
