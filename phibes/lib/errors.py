"""
Support functions for command-line interface modules.
"""

# core library modules

# third party packages

# in-project modules


class PhibesError(Exception):

    def __init__(self, *args):
        if args:
            self.message = f"Phibes error: {args[0]}"
        else:
            self.message = f"Phibes error: no more info"
        super().__init__(self.message)

    def __str__(self):
        msg = getattr(self, "message", "was raised")
        return f"{self.__class__}: {msg}"


class PhibesConfigurationError(PhibesError):
    pass


class PhibesAuthError(PhibesError):
    pass


class PhibesNotFoundError(PhibesError):
    pass


class PhibesExistsError(PhibesError):
    pass
