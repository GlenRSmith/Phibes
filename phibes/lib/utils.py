"""
Various helpful bits
"""

# Built-in library packages
from typing import Optional

# Third party packages

# In-project modules


def class_has_callable(
        cls,
        method: str,
        abstract: Optional[bool] = None
) -> bool:
    """
    Helper function to see if a class has a specified method
    If `abstract` is True, this function will require `method` to be abstract.
    If `abstract` is False, this function will forbid `method` to be abstract.
    If `abstract` is None, the function doesn't care whether `method` is
    abstract.
    @param cls: The class to test
    @type cls: type
    @param method: the name of the method to test
    @param abstract: whether to require/forbid/ignore the method to be abstract
    @return: Whether `cls` has a callable `method` matching `abstract`
    """
    is_abs = "__isabstractmethod__"
    return (
        hasattr(cls, method)
        and callable(getattr(cls, method))
        and (
            not abstract
            or (
                hasattr(getattr(cls, method), is_abs)
                and getattr(getattr(cls, method), is_abs)
            )
        )
        and (
            abstract is None
            or abstract
            or (
                not hasattr(getattr(cls, method), is_abs)
                or not getattr(getattr(cls, method), is_abs, True)
            )
        )
    )
