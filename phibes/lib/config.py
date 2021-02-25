"""
Package configuration
"""


# Built-in library packages
import enum
import json
from os import environ
from pathlib import Path
from typing import Optional, Union

# Third party packages
# In-project modules
from phibes.lib.errors import PhibesConfigurationError
from phibes.lib.utils import get_debug_info, get_path_tail


CONFIG_FILE_NAME = '.phibes.cfg'
DEFAULT_STORE_PATH = '.phibes'
count = 0
none_recs = {}
all_recs = {}


class StoreType(enum.Enum):
    FileSystem = 'FileSystem'


DEFAULT_STORE_TYPE = StoreType.FileSystem


class ConfigModel(object):
    """
    Configuration model class
    """
    @property
    def store_path(self) -> Optional[Path]:
        """
        Accessor for configuration store path
        :return: protected _store_path attribute
        """
        if self._store_path is None:
            self._store_path = Path(environ.get('PHIBES_STORE_PATH', None))
            # raise PhibesConfigurationError(f'{self._store_path=}')
            # raise PhibesConfigurationError('store_path not set')
        return self._store_path

    @store_path.setter
    def store_path(self, new_val: Optional[Union[Path, str]]):
        """
        Mutator for configuration store path
        :param new_val: new path to assign
        :return: None
        """
        if type(new_val) is str:
            new_val = Path(new_val)
        self._validate_store_path(new_val)
        self._store_path = new_val
        environ['PHIBES_STORE_PATH'] = f"{self._store_path}"

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

    def __init__(
            self,
            # store_path: Union[Path, str] = None,
            **kwargs
    ):
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
        self._store_path = None
        required = []
        optional = ['store_path']
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

        limit_calls = False
        arg_val = kwargs.get('store_path', None)
        if arg_val is None:
            self.store_path = environ.get("PHIBES_STORE_PATH", None)
            if debugging:
                none_recs[count] = all_recs[count]
                buffer = ' ' * 5
                msg = (
                    f'{buffer}{count=}{buffer}'
                    f'{buffer}{json.dumps(all_recs, indent=4)}{buffer}'
                )
                if count > 12 and limit_calls:
                    raise PhibesConfigurationError(msg)
            # pytest-of-gsmith/pytest-1074/test_normal0
            # try:
            #     self._set_private_property(
            #         name='store_path', value=None, optional=True
            #     )
            # except Exception as err:
            #     all_recs[count]['err'] = f"{err}"
        else:
            self.store_path = arg_val

        # These two 'work' when store_path is a function param
        # if store_path is None:
        #     self.store_path = environ.get("PHIBES_STORE_PATH", None)
        # else:
        #     self.store_path = store_path
        # self.store_path = (
        #     store_path, environ.get("PHIBES_STORE_PATH", None)
        # )[store_path is None]

        self.apply()

    def __str__(self):
        """
        Override the string representation of config
        """
        # Some things are not json serializable, e.g. Path
        ret_val = {
            "store_path": str(self.store_path.resolve())
        }
        return json.dumps(ret_val, indent=4)

    def __repr__(self):
        # Some things are not json serializable, e.g. Path
        ret_val = {
            "store_path": str(self.store_path.resolve())
        }
        return json.dumps(ret_val, indent=4)

    @staticmethod
    def _validate_store_path(val: Optional[Path]):
        if val is None:
            return
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
            self.store_path = self._store_path
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
        )
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
