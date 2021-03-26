"""
Code related to generating various representation of entities
"""

# Built-in library packages
from copy import deepcopy
import enum
import functools
import json

# Third party packages
# In-project modules
from phibes.lib.utils import todict


class ReprType(enum.Enum):
    Text = 'Text'
    JSON = 'JSON'
    HTML = 'HTML'
    Object = 'Object'


def to_html(content: str):
    return f'<span>{content}</span>'


ConversionMap = {
    ReprType.Object: {ReprType.JSON: [todict]},
    ReprType.JSON: {ReprType.Text: [json.dumps]},
    ReprType.Text: {ReprType.HTML: [to_html]}
}
path_cache = deepcopy(ConversionMap)


def find_conversion(
        from_type: ReprType, to_type: ReprType, visited: set = None
):
    """
    Returns a path of executable steps to convert an entity
    from `from_type` to `to_type`
    @param from_type:
    @param to_type:
    @param visited:
    @return:
    """
    global path_cache
    visited = (visited, set())[visited is None]
    if visited == set(path_cache.keys()):
        raise ValueError('every path has been tried')
    visited.add(from_type)
    if to_type == from_type:
        return []
    if to_type in path_cache[from_type]:
        # We already have a formula for this conversion
        return path_cache[from_type][to_type]
    else:
        best_path = []
        best_target = None
        # Types we do know how to convert to
        for avail_type in path_cache[from_type]:
            if avail_type not in visited:
                # Do we know how to get from _this_ one to target type?
                sub_steps = find_conversion(avail_type, to_type, visited)
                # Find and keep the one with the fewest steps
                if sub_steps:
                    if not best_path or len(sub_steps) < len(best_path):
                        best_path = sub_steps
                        best_target = avail_type
        if best_target:
            # that that path and insert our step from this type to that one
            new_path = path_cache[from_type][best_target] + best_path
            # we learned a new path, remember it
            path_cache[from_type][to_type] = new_path
            return new_path


def render(origin, from_type: ReprType, to_type: ReprType):
    """
    Returns a representation of `origin` in the requested `to_type`,
    provided there is a known conversion path from_type to_type
    @param origin: Entity to be represented
    @param from_type: current representation of origin
    @param to_type: desired representation
    @return: converted origin, or raised exception
    """
    steps = find_conversion(
        from_type=from_type, to_type=to_type, visited=set()
    )
    if steps or steps == []:
        step_val = origin
        for step in steps:
            step_val = step(step_val)
        return step_val
    else:
        raise ValueError(f'no conversion {from_type=} - {to_type}')


def rendered(func):
    """
    Decorator for functions that return 'business objects', but callers
    may want other representations instead.
    Any such decorated functions can receive a kwarg 'repr': ReprType
    to indicate the representation requested by the caller
    """
    @functools.wraps(func)
    def wrapped(**kwargs):
        return render(
            origin=func(**kwargs),
            from_type=ReprType.Object,
            to_type=kwargs.get('repr', ReprType.Object)
        )
    return wrapped
