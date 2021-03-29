"""
Package configuration
"""


# Built-in library packages
import json
from os import environ
from pathlib import Path
from typing import Optional

# Third party packages
# In-project modules
from phibes.lib.errors import PhibesConfigurationError
from phibes.lib.utils import get_debug_info, get_path_tail
from phibes.lib.utils import todict
from phibes.storage.types import StoreType


CONFIG_FILE_NAME = '.phibes.cfg'
DEFAULT_STORE_PATH = '.phibes'
count = 0
none_recs = {}
all_recs = {}


class ConfigModel(object):
    """
    Configuration model class
    """

    @property
    def store(self) -> dict:
        """
        Accessor for configured storage
        :return: protected _store attribute
        """
        ret_val = {'store_type': environ['PHIBES_STORE_TYPE']}
        if ret_val['store_type'] == StoreType.FileSystem.name:
            ret_val['store_path'] = environ['PHIBES_FILE_STORE_PATH']
        return ret_val

    @store.setter
    def store(self, val):
        # Have to flatten for environ
        if val is None:
            return
        if val['store_type'] == StoreType.FileSystem.name:
            self._validate_store_path(val['store_path'])
            environ['PHIBES_STORE_TYPE'] = StoreType.FileSystem.name
            environ['PHIBES_FILE_STORE_PATH'] = f"{val['store_path']}"
        else:
            environ['PHIBES_STORE_TYPE'] = val['store_type']
        self._store = val

    def _set_private_property(
            self, name: str, value=None, optional: bool = False
    ):
        if value is not None:
            setattr(self, name, value)
        else:
            if optional:
                setattr(self, f'_{name}', value)
            else:
                # let the property mutator complain
                setattr(self, f'{name}', value)

    def __init__(self, **kwargs):
        """
        Create a config object
        @param store_path: overriding store_path
        """
        global count, none_recs, all_recs
        debugging = False
        if debugging:
            count += 1
            spa = kwargs.get('store_path', None)
            if isinstance(spa, Path):
                spa = spa.resolve()
            if spa:
                spa = get_path_tail(pth=Path(spa), number_of_nodes=3)
            else:
                spa = ' no kwarg `store_path` '
            tmp_pth = environ.get('PHIBES_STORE_PATH', None)
            if tmp_pth:
                tmp_pth = get_path_tail(
                    pth=Path(tmp_pth), number_of_nodes=3
                )
            else:
                tmp_pth = ' no env var `PHIBES_STORE_PATH` '
            trace, trace_depth = get_debug_info(
                message='ConfigModel.__init__',
                start_frame=1, num_frames=12, stop_val='tests/conftest.py'
            )
            all_recs[count] = {
                'kwarg_keys': ','.join(list(kwargs.keys())),
                'store_path_arg': spa, 'env_store_path': tmp_pth,
                'trace': trace, 'trace_depth': trace_depth
            }
            key_list = list(kwargs.keys())
            all_recs[count]['kwarg_keys'] = (
                ', '.join(key_list), ' no kwargs passed '
            )[not key_list]

        # Prevent IDE from complaining elsewhere about assignment
        self._store = None
        required = []
        optional = ['store']
        err_list = []
        for name in optional + required:
            arg_val = kwargs.get(name, None)
            try:
                self._set_private_property(
                    name=name,
                    value=arg_val,
                    optional=(name not in required)
                )
            except Exception as err:
                err_list.append(err)
        if err_list:
            raise PhibesConfigurationError(f'missing arg(s): {err_list}')
        self.apply()

    def __str__(self):
        """
        Override the string representation of config
        """
        # Some things are not json serializable, e.g. Path
        ret_val = {"store": self.store}
        return json.dumps(todict(ret_val), indent=4)

    def __repr__(self):
        # Some things are not json serializable, e.g. Path
        ret_val = {"store": self.store}
        return json.dumps(todict(ret_val), indent=4)

    @staticmethod
    def _validate_store_path(val: Optional[Path]):
        if val is None:
            return
        if type(val) is str:
            val = Path(val)
        if not isinstance(val, Path):
            raise PhibesConfigurationError(
                f"store_path must be a Path, {val} is {type(val)}"
            )
        if not val.exists():
            try:
                val.mkdir()
            except FileNotFoundError:
                raise PhibesConfigurationError(
                    f"store_path {val} does not exist"
                )
        return

    def validate(self):
        failures = []
        # Trigger the field validation in each property mutator
        try:
            self.store = self._store
        except TypeError as err:
            failures.append(f"{err}\n")
        if failures:
            raise PhibesConfigurationError(failures)
        return True

    def apply(self):
        """
        Make the values in this instance the "live" config
        """
        self.validate()


def load_config_file(path: Path) -> ConfigModel:
    """
    Read a config path, set the environment from it, return the ConfigModel.
    @param path: the config file, or directory containing it
    @return: The newly-loaded ConfigModel
    """
    if not path.exists():
        raise FileNotFoundError(f"{path.absolute()} not found")
    if path.is_dir():
        parent_dir = path
        conf_file = path.joinpath(CONFIG_FILE_NAME)
    elif path.is_file():
        parent_dir = path.parent
        conf_file = path
    else:
        raise PhibesConfigurationError(
            f"{path} must be an existing directory or a file"
        )
    with conf_file.open('r') as cf:
        conf_dict = json.loads(cf.read())
    conf_mod = ConfigModel(
        store_path=conf_dict.get(
            'store_path', Path.joinpath(parent_dir, DEFAULT_STORE_PATH)
        ),
        store=conf_dict.get('store')
    )
    conf_mod.apply()
    return conf_mod


def write_config_file(
        path, config_model=None, update=False, bypass_validation=False
):
    """
    Write a config to a path
    With no config_model, write the values currently in the environment
    """
    if config_model is None:
        config_model = ConfigModel()
    if not bypass_validation:
        config_model.validate()
    if path.exists():
        if path.is_dir():
            conf_file = path.joinpath(CONFIG_FILE_NAME)
        elif path.is_file():
            conf_file = path
        else:
            raise PhibesConfigurationError(
                f"{path} must be a directory or a file"
            )
    elif path.name == CONFIG_FILE_NAME and path.parent.exists():
        conf_file = path
    else:
        raise ValueError(f"can not resolve {path}")
    if conf_file.exists() and not update:
        raise FileExistsError(f"{conf_file} already exists, `update` required")
    if update and not conf_file.exists():
        raise FileNotFoundError(f"{conf_file} not found, can't `update`.")
    try:
        conf_file.write_text(f"{config_model}")
    except FileNotFoundError:
        raise
    return
