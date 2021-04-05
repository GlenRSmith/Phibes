"""
Click options for click commands
"""

# core library modules
import getpass
import pathlib

# third party packages
import click

# in-project modules
from phibes.cli.cli_config import CLI_CONFIG_FILE_NAME, get_home_dir
from phibes.cli.cli_config import DEFAULT_EDITOR
from phibes.crypto import default_id, list_crypts
from phibes.lib.config import DEFAULT_STORE_PATH


class MappedChoices(object):
    """
    Utility class that enables verbose prompt showing each choice while
    allowing a simple numeric entry for selection
    """
    def __init__(
            self, prompt: str, choices: list, default_val: str, help: str
    ):
        self.default_choice = None
        self.prompt = prompt
        self.help = help
        # create a dict of integer keys to 'choices'
        self.choice_dict = dict(
            zip([str(i) for i in list(range(len(choices)))], choices)
        )
        for k, v in self.choice_dict.items():
            if v == default_val:
                self.default_choice = k
                self.prompt += f"{k}: {v}*\n"
            else:
                self.prompt += f"{k}: {v}\n"
        if not self.default_choice:
            raise ValueError(f"{default_val} missing from {choices}")
        self.choice = click.Choice(list(self.choice_dict.keys()))
        return

    def get_click_option(self, opt_str: str) -> click.Option:
        """
        returns a click command option configured with values passed to c'tor
        :param opt_str: the `--` option string for this option
        :return: click option
        """
        return click.option(
            opt_str,
            type=self.choice,
            prompt=self.prompt,
            help=self.help,
            default=self.default_choice
        )

    def update_choices(self, ctx: click.Context, target_name: str):
        """
        Modifies the named command option in the passed context
        using the property values of this instance
        :param ctx: context
        :param target_name: name of option to modify
        :return:
        """
        for p in ctx.command.params:
            if p.name == target_name:
                p.type = self.choice
                p.prompt = self.prompt
                p.default = self.default_choice


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


crypt_choices = MappedChoices(
    prompt='Crypt ID (accept default)\n',
    choices=list_crypts(),
    default_val=default_id,
    help="Encryption type, usually best to accept default"
)
crypt_option = crypt_choices.get_click_option("--crypt_id")
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
    help="Name of locker, defaults to OS username. Will be encoded "
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
cli_config_file_option = click.option(
    '--path',
    prompt='Path to config file',
    help=f'Path on filesystem for config file {CLI_CONFIG_FILE_NAME}',
    type=pathlib.Path,
    default=get_home_dir().joinpath(CLI_CONFIG_FILE_NAME)
)
store_path_option = click.option(
    '--store_path',
    prompt='Path to locker(s)',
    help='Path on filesystem where encrypted data will be written',
    type=pathlib.Path,
    default=get_home_dir().joinpath(DEFAULT_STORE_PATH)
)
editor_option = click.option(
    '--editor',
    prompt='editor (for adding/updating encrypted items)',
    help='shell-invocable editor to use with the `edit` command',
    type=str,
    default=DEFAULT_EDITOR
)
config_option = click.option(
    '--config',
    default=get_home_dir().joinpath(CLI_CONFIG_FILE_NAME),
    type=pathlib.Path,
    help=(
        f"Path to config file `{CLI_CONFIG_FILE_NAME}`, "
        f"defaults to user home"
    ),
    show_envvar=True,
    envvar="PHIBES_CONFIG",
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
