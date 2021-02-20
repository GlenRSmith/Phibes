#!/usr/bin/env python
"""
Click-based command-line interface to phibes
"""
# core library modules
# third party packages
# in-project modules
from phibes.cli.commands import build_cli_app
from phibes.cli.commands import Action, Target
from phibes.cli.config.create import create_config_cmd
from phibes.cli.config.update import update_config_cmd
from phibes.cli import handlers
from phibes.cli.lib import main, main_func

command_dict = {
    Target.Locker: {
        Action.Create: {'name': 'create', 'func': handlers.create_locker},
        Action.Get: {'name': 'info', 'func': handlers.get_locker},
        Action.Delete: {'name': 'delete', 'func': handlers.delete_locker},
    },
    Target.Item: {
        Action.Create: {'name': 'create-item', 'func': handlers.create_item},
        Action.Get: {'name': 'get-item', 'func': handlers.get_item},
        Action.Update: {'name': 'edit', 'func': handlers.edit_item},
        Action.List: {'name': 'list', 'func': handlers.get_items},
        Action.Delete: {'name': 'delete-item', 'func': handlers.delete_item}
    }
}
build_cli_app(command_dict=command_dict, click_group=main, named_locker=True)
main.add_command(create_config_cmd)
main.add_command(update_config_cmd)


if __name__ == '__main__':
    main_func()
