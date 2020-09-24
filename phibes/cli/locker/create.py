"""
Click interface to create Locker
"""

# core library modules

# third party packages
import click

# in-project modules
from phibes.cli.command_base import ConfigFileLoadingCmd
from phibes.crypto import default_id, list_crypts
from phibes.lib.errors import PhibesExistsError
from phibes.cli.lib import PhibesCliExistsError
from phibes.model import Locker


class CryptChoices:
    """
    Utility class that enables verbose prompt for crypt-id choice while
    allowing a simple numeric entry for selection
    """

    def __init__(self, choices: list, default_val: str):
        self.choices = []
        self.default_choice = None
        self.prompt = ''
        self.choice_dict = dict(
            zip([str(i) for i in list(range(len(choices)))], choices)
        )
        for k, v in self.choice_dict.items():
            self.choices.append(k)
            if v == default_val:
                self.default_choice = k
                self.prompt += f"{k}: {v}*\n"
            else:
                self.prompt += f"{k}: {v}\n"
        if not self.default_choice:
            raise ValueError(f"{default_val} missing from {choices}")
        return


crypt_choices = CryptChoices(list_crypts(), default_id)


class CreateLockerCmd(ConfigFileLoadingCmd):

    def __init__(self):
        super(CreateLockerCmd, self).__init__()
        return

    @staticmethod
    def handle(config, locker, password, crypt_id, *args, **kwargs):
        super(CreateLockerCmd, CreateLockerCmd).handle(
            config, *args, **kwargs
        )
        try:
            new_locker = Locker.create(
                locker, password, crypt_choices.choice_dict[crypt_id]
            )
        except PhibesExistsError as err:
            raise PhibesCliExistsError(
                f"Locker {locker} already exists\n{err}"
            )
        click.echo(f"Locker created {locker}")
        click.echo(f"Locker created {new_locker.path}")
        return


options = {
    'password': click.option(
        '--password',
        prompt='Locker Password',
        hide_input=True,
        confirmation_prompt=True
    ),
    'crypt_id': click.option(
        '--crypt_id',
        prompt='Crypt ID (accept default)\n' + crypt_choices.prompt,
        type=click.Choice(crypt_choices.choices),
        default=crypt_choices.default_choice
    )
}


create_locker_cmd = CreateLockerCmd.make_click_command(
    'create-locker', options
)
