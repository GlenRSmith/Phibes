"""
Click command for `create-item`
"""

# core library modules
# third party packages
# in-project modules
from phibes.cli.command_base import ConfigFileLoadingCmd, PhibesCommandBareBase
from phibes.cli.command_base import config_option
from phibes.cli.errors import PhibesCliError
from phibes.cli.lib import create_item, get_locker_args, create_item_new
from phibes.cli.options import item_name_option, template_name_option
from phibes.cli.options import locker_name_option, locker_path_option
from phibes.cli.options import password_option


class NewCreateItemCmd(PhibesCommandBareBase):
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
        super(NewCreateItemCmd, self).__init__()

    @staticmethod
    def handle(*args, **kwargs) -> None:
        """Create and add an item to a locker"""
        super(NewCreateItemCmd, NewCreateItemCmd).handle(*args, **kwargs)
        template = kwargs.get('template', None)
        if template == 'Empty':
            template = None
        try:
            item_name = kwargs.pop('item')
        except KeyError as err:
            raise PhibesCliError(f'missing required param {err}')
        inst = get_locker_args(*args, **kwargs)
        return create_item_new(
            locker=inst, item_name=item_name, template_name=template
        )


class CreateItemNamedLockerCmd(NewCreateItemCmd):

    options = {
        'config': config_option,
        'locker': locker_name_option,
        'password': password_option,
        'item': item_name_option,
        'template': template_name_option
    }

    def __init__(self):
        super(CreateItemNamedLockerCmd, self).__init__()


class CreateItemCmd(ConfigFileLoadingCmd):
    """
    Command to create a new item in a locker
    """

    def __init__(self):
        super(CreateItemCmd, self).__init__()
        return

    @staticmethod
    def handle(
            config,
            locker,
            password,
            item,
            template,
            *args, **kwargs
    ):
        """
        Launch editor to create/update an item in a locker

        :param config:
        :param locker:
        :param password:
        :param item:
        :param template:
        :return:
        """
        super(CreateItemCmd, CreateItemCmd).handle(
            config, *args, **kwargs
        )
        if template == 'Empty':
            template = None
        return create_item(locker, password, item, template)


options = {
    'item': item_name_option,
    'template': template_name_option
}

create_item_cmd = CreateItemNamedLockerCmd.make_click_command('create-item')
# create_item_cmd = CreateItemCmd.make_click_command('create-item', options)
