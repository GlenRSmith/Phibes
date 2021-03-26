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
            self.message = "Phibes error: no more info"
        super().__init__(self.message)

    def __str__(self):
        msg = getattr(self, "message", "was raised")
        return f"{self.__class__}: {msg}"


class PhibesConfigurationError(PhibesError):
    """
    Custom error for configuration problem
    """
    pass


class PhibesAuthError(PhibesError):
    """
    Custom error for failed auth attempt
    """
    pass


class PhibesNotFoundError(PhibesError):
    """
    Custom error for something not found
    """
    pass


class PhibesExistsError(PhibesError):
    """
    Custom error for something unexpectedly already existing
    """
    pass


class PhibesUnknownError(PhibesError):
    """
    Custom error for problem detected but not categorized
    """
    pass
