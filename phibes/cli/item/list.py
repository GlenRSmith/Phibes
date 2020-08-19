"""
Click interface to phibes items
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.lib import get_config, get_locker, make_click_command
from phibes.cli.lib import present_list_items
from phibes.lib.locker import registered_items


options = {
    'item-type': click.option(
        '--item_type',
        prompt='Type of item to list',
        help='Type of item to list - default `all`',
        type=click.Choice(list(registered_items.keys()) + ['all']),
        default='all'
    ),
    'verbose': click.option(
        '--verbose',
        prompt='Verbose',
        help='Present entire contents of each item',
        default=False,
        type=bool
    )
}


# @click.command(name='list')
# @click.option(
#     '--item_type',
#     prompt='Type of item to list',
#     type=click.Choice(list(registered_items.keys()) + ['all']),
#     default='all'
# )
# @click.option('--verbose', prompt='Verbose', default=False, type=bool)
def list_items(config, locker, password, item_type, verbose):
    """
    Display the (unencrypted) names of all Secrets in the Locker
    :param item_type:
    :param verbose:
    :return:
    """
    user_config = get_config(config)
    click.echo(
        present_list_items(locker, password, item_type, verbose)
    )
    return


list_items_cmd = make_click_command('list', list_items, options)


@click.command()
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
@click.option(
    '--item_type',
    prompt='Type of item to list',
    type=click.Choice(list(registered_items.keys()) + ['all']),
    default='all'
)
@click.option('--verbose', prompt='Verbose', default=False, type=bool)
def ls(locker, password, item_type, verbose):
    click.secho(
        present_list_items(locker, password, item_type, verbose),
        fg='green'
    )
    return
