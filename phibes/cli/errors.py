"""
Command-line interface error definitions
"""

# core library modules
import getpass
import os
import pathlib

# third party packages
import click

# in-project modules
from phibes.lib.config import ConfigModel, CONFIG_FILE_NAME
from phibes.lib.config import get_editor, get_home_dir
from phibes.lib import errors
from phibes.lib.errors import PhibesNotFoundError
from phibes.model import Locker


class PhibesCliError(errors.PhibesError):

    def __init__(self, *args):
        if args:
            self.message = f"Phibes error: {args[0]}"
        else:
            self.message = f"Phibes error: no more info"
        super().__init__(self.message)

    def __str__(self):
        msg = getattr(self, "message", "was raised")
        return f"{self.__class__}: {msg}"


class PhibesCliNotFoundError(PhibesCliError):
    pass


class PhibesCliExistsError(PhibesCliError):
    pass


class PhibesCliPasswordError(PhibesCliError):
    pass
