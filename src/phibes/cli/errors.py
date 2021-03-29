"""
Command-line interface error definitions
"""

# core library modules
# third party packages
# in-project modules
from phibes.lib import errors


class PhibesCliError(errors.PhibesError):

    def __init__(self, *args):
        if args:
            self.message = f"Phibes error: {args[0]}"
        else:
            self.message = "Phibes error: no more info"
        super().__init__(self.message)

    def __str__(self):
        msg = getattr(self, "message", "was raised")
        return f"{self.__class__}: {msg}"


class PhibesCliConfigurationError(PhibesCliError):
    pass


class PhibesCliNotFoundError(PhibesCliError):
    pass


class PhibesCliExistsError(PhibesCliError):
    pass


class PhibesCliPasswordError(PhibesCliError):
    pass
