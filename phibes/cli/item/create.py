"""
Click command for `create-item`
"""

# core library modules
# third party packages
# in-project modules
from phibes.cli.command_base import PhibesCommand
from phibes.cli.command_base import config_option
from phibes.cli.errors import PhibesCliError
from phibes.cli.lib import get_locker_args, create_item
from phibes.cli.options import item_name_option, template_name_option
from phibes.cli.options import locker_name_option, locker_path_option
from phibes.cli.options import password_option


class CreateItemCommand(PhibesCommand):
    """
    Class to create and run click command to create and add an item to a locker
    """

    options = {
        'config': config_option,
        'path': locker_path_option,
        'password': password_option,
        'item': item_name_option,
        'template': template_name_option
    }

    def __init__(self):
        super(CreateItemCommand, self).__init__()

    @staticmethod
    def handle(*args, **kwargs) -> None:
        """Create and add an item to a locker"""
        super(CreateItemCommand, CreateItemCommand).handle(*args, **kwargs)
        template = kwargs.get('template', None)
        if template == 'Empty':
            template = None
        try:
            item_name = kwargs.pop('item')
        except KeyError as err:
            raise PhibesCliError(f'missing required param {err}')
        inst = get_locker_args(*args, **kwargs)
        return create_item(
            locker=inst, item_name=item_name, template_name=template
        )


class CreateItemNamedLockerCmd(CreateItemCommand):

    options = {
        'config': config_option,
        'locker': locker_name_option,
        'password': password_option,
        'item': item_name_option,
        'template': template_name_option
    }

    def __init__(self):
        super(CreateItemNamedLockerCmd, self).__init__()
