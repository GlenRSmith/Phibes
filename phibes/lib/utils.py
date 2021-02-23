"""
Various helpful bits
"""

# Built-in library packages
import collections
import enum
from typing import Optional

# Third party packages
# In-project modules


class ReprType(enum.Enum):
    Text = 'Text'
    JSON = 'JSON'
    HTML = 'HTML'
    Object = 'Object'


# def todict(obj, classkey=None):
#     if isinstance(obj, dict):
#         data = {}
#         for (k, v) in obj.items():
#             data[k] = todict(v, classkey)
#         return data
#     elif hasattr(obj, "_ast"):
#         return todict(obj._ast())
#     elif hasattr(obj, "__iter__") and not isinstance(obj, str):
#         return [todict(v, classkey) for v in obj]
#     elif hasattr(obj, "__dict__"):
#         data = dict([(key, todict(value, classkey))
#             for key, value in obj.__dict__.items()
#             if not callable(value) and not key.startswith('_')])
#         if classkey is not None and hasattr(obj, "__class__"):
#             data[classkey] = obj.__class__.__name__
#         return data
#     else:
#         return str(obj)


def todict(obj):
    """
    Recursively convert a Python object graph to sequences (lists)
    and mappings (dicts) of primitives (bool, int, float, string, ...)
    """
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, dict):
        return dict((key, todict(val)) for key, val in obj.items())
    elif isinstance(obj, collections.Iterable):
        return [todict(val) for val in obj]
    elif hasattr(obj, '__dict__'):
        return todict(vars(obj))
    elif hasattr(obj, '__slots__'):
        return todict(
            dict(
                (
                    name,
                    getattr(obj, name)
                ) for name in getattr(obj, '__slots__')
            )
        )
    return str(obj)


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
    @param method: the locker_id of the method to test
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


def validate_child(parent_class, candidate_child_class):
    """

    :param parent_class:
    :type parent_class:
    :param candidate_child_class:
    :type candidate_child_class:
    :return:
    :rtype:
    """
    if not parent_class.__subclasshook__(candidate_child_class):
        missing = {
            name for name in dir(parent_class)
            if class_has_callable(
                parent_class, name, abstract=True
            )
        } - {
            name for name in dir(parent_class)
            if class_has_callable(
                candidate_child_class, name, abstract=False
            )
        }
        raise ValueError(
            f"{candidate_child_class} is missing implementation for {missing}"
        )
    return
