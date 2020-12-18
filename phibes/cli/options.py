"""
Click options for click commands
"""

# core library modules
import getpass
import pathlib

# third party packages
import click

# in-project modules


def validate_locker_path(
        ctx: click.Context, param: click.Option, value: pathlib.Path
):
    """
    Custom validation rule for locker_path_option
    Additional validation is done in Locker depending on operation
    """
    if not value.exists():
        raise click.BadParameter(
            f"{value} path does not exist"
        )
    return value


def validate_password(
        ctx: click.Context, param: click.Option, value: str
):
    """
    Custom validation rule for new_password_option
    """
    if len(value) < 3:
        raise click.BadParameter(
            "password must be a least 3 characters"
        )
    return value


def validate_item_name(
        ctx: click.Context, param: click.Option, value: str
):
    """
    Custom validation rule for item_name_option
    """
    # Possibly enforce max length, character set, or something
    return value


item_name_option = click.option(
    '--item',
    prompt='Item name',
    callback=validate_item_name,
    help='Name of item on which to perform this action',
)
template_name_option = click.option(
    '--template',
    prompt='Template name',
    help='Name of item to start with, can also be a text file',
    default='Empty'
)
locker_name_option = click.option(
    '--locker',
    prompt='Locker name',
    type=str,
    default=getpass.getuser(),
    help="Name of locker, defaults to local OS username"
)
locker_path_option = click.option(
    '--path',
    prompt='Locker path',
    default=pathlib.Path.cwd(),
    type=pathlib.Path,
    callback=validate_locker_path,
    help="Path to locker, defaults to current working directory"
)
new_password_option = click.option(
    '--password',
    prompt='Locker Password',
    hide_input=True,
    confirmation_prompt=True,
    callback=validate_password,
    help="Enter new password (input is hidden)"
)
password_option = click.option(
    '--password',
    prompt='Password',
    help='Password used when Locker was created',
    hide_input=True
)
user_password_option = click.option(
    '--user_password',
    prompt='User Password',
    help="User's main phibes password",
    hide_input=True
)
new_user_password_option = click.option(
    '--user_password',
    prompt='User Password',
    hide_input=True,
    confirmation_prompt=True
)
verbose_item_option = click.option(
    '--verbose',
    prompt='Verbose',
    help='Present entire contents of each item',
    default=False,
    type=bool
)

env_vars = {
    'editor': 'PHIBES_EDITOR'
}
env_options = {}
for var in env_vars:
    var_option = click.option(
        f"--{var}",
        help=(
            f'Sets the env value for {env_vars[var]} '
            f'for the duration of the command'
        )
    )
    env_options[var] = var_option
