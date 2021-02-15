"""
Click interface to get Locker
"""
# core library modules
# third party packages
import click

# in-project modules
from phibes.cli.command_base import PhibesCommandBareBase
from phibes.cli.command_base import config_option
from phibes.cli.lib import get_locker_args
from phibes.cli.options import locker_name_option
from phibes.cli.options import locker_path_option
from phibes.cli.options import password_option


class GetLockerCmd(PhibesCommandBareBase):
    """
    Class to create and run click command to get a locker
    """

    options = {
        'config': config_option,
        'path': locker_path_option,
        'password': password_option
    }

    def __init__(self):
        super(GetLockerCmd, self).__init__()

    @staticmethod
    def handle(*args, **kwargs):
        """Get a Locker"""
        # parent class sets up environment variables from args
        super(GetLockerCmd, GetLockerCmd).handle(*args, **kwargs)
        inst = get_locker_args(*args, **kwargs)
        if inst.path.exists():
            click.echo(f"confirmed locker dir {inst.path} exists")
        if inst.lock_file.exists():
            click.echo(f"confirmed lock file {inst.lock_file} exists")
            click.echo(f"Lock file {inst.lock_file}")
            click.echo(f"Created {inst.timestamp}")
            click.echo(f"Crypt ID {inst.crypt_impl.crypt_id}")
        return inst


class GetNamedLockerCmd(GetLockerCmd):
    """
    Class to create and run click command to delete a named locker
    """

    options = {
        'config': config_option,
        'locker': locker_name_option,
        'password': password_option
    }

    def __init__(self):
        super(GetNamedLockerCmd, self).__init__()
