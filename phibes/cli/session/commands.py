"""
Click commands for phibes command-line session
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.lib.locker import Locker
from phibes.lib import shell_session


@click.command()
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
def set_session(locker, password):
    if Locker.find(locker, password):
        shell_session.set_session(locker, password)
    else:
        click.echo("Matching locker not found")
    return


@click.command()
def clear_session():
    shell_session.clear_session()
    return
