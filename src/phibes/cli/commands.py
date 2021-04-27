"""
Click interface
"""
# core library modules
# third party packages
import click
import enum

# in-project modules
from phibes.cli import handlers
from phibes.cli.options import cli_config_file_option
from phibes.cli.options import config_option
from phibes.cli.options import editor_option
from phibes.cli.options import env_options
from phibes.cli.options import crypt_option
from phibes.cli.options import item_name_option
from phibes.cli.options import locker_name_option
from phibes.cli.options import locker_path_option
from phibes.cli.options import new_password_option
from phibes.cli.options import password_option
from phibes.cli.options import store_path_option
from phibes.cli.options import template_name_option
from phibes.cli.options import verbose_item_option


class Target(enum.Enum):
    Locker = 'Locker'
    Item = 'Item'
    Config = 'Config'


class Action(enum.Enum):
    Create = 'Create'
    Update = 'Update'
    Delete = 'Delete'
    Get = 'Get'
    List = 'List'


ANON_COMMAND_DICT = {
    Target.Locker: {
        Action.Create: {'name': 'init', 'func': handlers.create_locker},
        Action.Get: {'name': 'status', 'func': handlers.get_locker},
        Action.Delete: {'name': 'delete', 'func': handlers.delete_locker},
    },
    Target.Item: {
        Action.Create: {'name': 'add', 'func': handlers.create_item},
        Action.Get: {'name': 'get', 'func': handlers.get_item},
        Action.Update: {'name': 'edit', 'func': handlers.edit_item},
        Action.List: {'name': 'list', 'func': handlers.get_items},
        Action.Delete: {'name': 'remove', 'func': handlers.delete_item}
    }
}

NAMED_COMMAND_DICT = {
    Target.Locker: {
        Action.Create: {'name': 'create', 'func': handlers.create_locker},
        Action.Get: {'name': 'info', 'func': handlers.get_locker},
        Action.Delete: {'name': 'delete', 'func': handlers.delete_locker},
    },
    Target.Item: {
        Action.Create: {
            'name': 'create-item', 'func': handlers.create_item
        },
        Action.Get: {'name': 'get-item', 'func': handlers.get_item},
        Action.Update: {'name': 'edit', 'func': handlers.edit_item},
        Action.List: {'name': 'list', 'func': handlers.get_items},
        Action.Delete: {
            'name': 'delete-item', 'func': handlers.delete_item
        }
    },
    Target.Config: {
        Action.Create: {
            'name': 'create-config', 'func': handlers.create_cli_config
        },
        Action.Update: {
            'name': 'update-config', 'func': handlers.update_cli_config
        }
    }
}


def make_command_handler(
        target: Target, action: Action, name_lockers: bool, name: str = None
) -> dict:
    src = (ANON_COMMAND_DICT, NAMED_COMMAND_DICT)[name_lockers]
    ret_val = src[target][action]
    if name:
        ret_val['name'] = name
    return ret_val


class PhibesClickCmd(object):

    def __init__(
            self, target: Target,
            action: Action,
            handler,
            named_locker: bool = True,
            init_options=None
            # I don't remember why I included init_options
            # As implemented, they are an override
            # I'll keep it around for a minute
    ):
        self.target = target
        self.action = action
        self.handler = handler
        # TODO: add validation of handler signature
        self.named_locker = named_locker
        self.init_options = init_options
        self._options = None
        self._command = None

    @property
    def options(self):
        if not self._options:
            if self.init_options:
                self._options = self.init_options
            else:
                if self.target == Target.Config:
                    cmd_opts = {
                        'path': cli_config_file_option,
                        'store_path': store_path_option,
                        'editor': editor_option
                    }
                else:
                    cmd_opts = {'password': password_option}
                    if self.named_locker:
                        cmd_opts['config'] = config_option
                        cmd_opts['locker'] = locker_name_option
                    else:
                        cmd_opts['path'] = locker_path_option
                    if self.target == Target.Item:
                        if self.action == Action.List:
                            cmd_opts['verbose'] = verbose_item_option
                        else:
                            cmd_opts['item'] = item_name_option
                    if self.action == Action.Create:
                        if self.target == Target.Locker:
                            cmd_opts['password'] = new_password_option
                            cmd_opts['crypt_id'] = crypt_option
                        elif self.target == Target.Item:
                            cmd_opts['template'] = template_name_option
                # env_options exposes the ability to specify any option
                # on command line, but none of them are prompted
                # Right now it is just "editor"
                cmd_opts.update(env_options)
                self._options = cmd_opts
        return self._options

    @property
    def command(self) -> click.Command:
        if not self._command:
            # Apply the options to the func, as click decorators do
            for option in reversed(self.options.values()):
                option(self.handler)
            self._command = click.command(
                context_settings=dict(max_content_width=120)
            )(self.handler)
            # TODO: wrap handler with implementation from class PhibesCommand
            # whatever the hell that meant when I wrote it.
        return self._command


def build_cli_app(command_dict, click_group, named_locker=False):
    for targ, val in command_dict.items():
        for act, rec in val.items():
            cmd = PhibesClickCmd(
                target=targ,
                action=act,
                handler=rec['func'],
                named_locker=named_locker
            ).command
            click_group.add_command(cmd, rec['name'])
