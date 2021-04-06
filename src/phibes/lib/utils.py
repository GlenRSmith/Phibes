"""
Various helpful bits
"""

# Built-in library packages
import base64
from collections.abc import Iterable
from inspect import getframeinfo, stack
from os import environ, path, sep
from pathlib import Path
from typing import Optional

# Third party packages
# In-project modules
from phibes.lib.errors import PhibesError


def todict(obj):
    """
    Recursively convert a Python object graph to sequences (lists)
    and mappings (dicts) of primitives (bool, int, float, string, ...)
    """
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, dict):
        return dict((key, todict(val)) for key, val in obj.items())
    elif isinstance(obj, Iterable):
        return [todict(val) for val in obj]
    elif isinstance(obj, Path):
        return str(obj)
    elif hasattr(obj, '__dict__'):
        resdict = {}
        for key, val in obj.__dict__.items():
            if callable(val):
                continue
            elif key.startswith('_'):
                try:
                    if hasattr(obj, key[1:]):
                        tk = key[1:]
                        tv = getattr(obj, tk)
                    else:
                        continue
                except TypeError as err:
                    raise TypeError(f'<   {err=}   ><   {key=}   >')
            else:
                tk = key
                tv = val
            try:
                resdict[tk] = todict(tv)
            except TypeError as err:
                raise TypeError(err)
        return resdict
    elif hasattr(obj, '__slots__'):
        return todict(
            dict(
                (name, getattr(obj, name))
                for name in getattr(obj, '__slots__')
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


def get_debug_info(
        message: str,
        start_frame: int = 1,
        num_frames: int = 3,
        stop_val: str = ''
):
    """
    Returns a string with call stack info
    Not documenting carefully because it's likely to be in flux,
    and is exclusively used for temporary debugging purposes
    @param message: Optional user message string for header
    @param start_frame: frame of stacktrace to start at
    @param num_frames: number of stacktrace frame to attempt to show
    @param stop_val: optional string to scan for to end before num_frames
    @return: the stacktrace string
    """
    ret_str = f" - {message} - "
    last_frame = 0
    match_msg = ""
    for frame_num in range(start_frame, start_frame + num_frames):
        last_frame = frame_num
        caller = getframeinfo(stack()[frame_num][0])
        pth = get_path_tail(
            pth=Path(caller.filename), number_of_nodes=2
        )
        ret_str += f" <({frame_num}):{pth}:{caller.lineno}> "
        if stop_val and stop_val in pth:
            match_msg = f"found {stop_val=}"
            break
    if match_msg:
        ret_str += match_msg
    else:
        ret_str += f"reached {num_frames=}"
    return ret_str, last_frame


def get_path_tail(pth: Path, number_of_nodes: int = 3) -> str:
    """returns the last n nodes of the path"""
    return sep.join(pth.parts[-number_of_nodes:])


def find_path_dupes(
        full_path: Path,
        number_of_nodes: int = 2,
        min_match_prefix: int = 9
) -> str:
    """
    Raises a custom exception if the Path has duplicate or
    near duplicate parts in sequence, otherwise, returns an abbreviated
    form of the Path
    @param full_path: Path to evaluate
    @param number_of_nodes: Number of path elements to include in return
    @param min_match_prefix: Minimum number of start chars for nodes to match
    @return: abbreviated path string
    """
    path_str = path.normpath(full_path)  # normalized path string
    node_list = path_str.split(sep)  # list of path pieces split by OS char
    for i in range(len(node_list) - 1):
        n0 = node_list[i]
        n1 = node_list[i + 1]
        if n0 == n1:
            msg = f"{n0} is repeated in {full_path}"
            di = get_debug_info(msg)
            raise DebugTraceReport(di)
        elif n0[0:min_match_prefix] == n1[0:min_match_prefix]:
            msg = f"<{n0=}><{n1=}><{full_path}>"
            di = get_debug_info(msg)
            raise DebugTraceReport(di)
    # string of the last n nodes
    return sep.join(node_list[-number_of_nodes:])


def get_envpath_tail(env_key: str, depth: int = 3) -> str:
    """
    Returns the last `depth` nodes of a Path from an environment variable
    Useful in troubleshooting
    """
    return get_path_tail(
        pth=Path(environ[env_key]), number_of_nodes=depth
    )


def encode_name(name: str) -> str:
    """
    Returns a base64-encoded string with padding stripped off.
    """
    return base64.urlsafe_b64encode(name.encode()).rstrip(b"=").decode()


def decode_name(encoded_name: str) -> str:
    """
    Returns a base64-decoded string from the encoded name
    """
    padding = 4 - (len(encoded_name.encode()) % 4)
    return base64.urlsafe_b64decode(
        encoded_name.encode() + (b"=" * padding)
    ).decode()


class DebugTraceReport(PhibesError):
    pass
