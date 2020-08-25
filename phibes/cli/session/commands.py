"""
Click commands for phibes command-line session
"""

# core library modules
from os import environ
import pathlib

# third party packages
import click

# in-project modules
from phibes.lib.locker import Locker


default_file_name = ".phibes.conf"


def set_config(file_path: pathlib.Path):
    #
    # try to read the file
    if file_path.is_dir():
        conf_file = file_path.joinpath(default_file_name)
    elif file_path.is_file():
        conf_file = file_path
    else:
        raise ValueError(f"that is not a good Path object")
    contents = conf_file.read_text()
    return



def test(key, value):
    env_key = f"{key}"
    env_val = environ[env_key]
    print(f"{env_val} - {value}")


@click.command()
@click.option('--locker', prompt='Locker')
@click.option('--password', prompt='Password', hide_input=True)
def set_session(locker, password):
    # if Locker.find(locker, password):
    #     shell_session.set_session(locker, password)
    # else:
    #     click.echo("Matching locker not found")
    return


@click.command()
def clear_session():
    # shell_session.clear_session()
    return
