"""
Package configuration
"""


# Built-in library packages
import json
from os import environ
from pathlib import Path
from typing import Union

# Third party packages

# In-project modules
# Be very cautious here not to introduce cyclic imports
from phibes.lib.errors import PhibesConfigurationError

# TODO: provide server config, this is mostly single user, local CLI config


CONFIG_FILE_NAME = '.phibes.cfg'
DEFAULT_STORE_PATH = '.phibes'
DEFAULT_EDITOR = environ.get('EDITOR', 'unknown')
DEFAULT_HASH_LOCKER_NAMES = True
HOME_DIR = None


def get_home_dir() -> Path:
    """
    This allows changing the home dir without changing the command
    interface. It simplifies configuring testing to not use user's home.
    """
    global HOME_DIR
    if not HOME_DIR:
        HOME_DIR = Path.home()
    return HOME_DIR


def set_home_dir(path: Path) -> None:
    global HOME_DIR
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    HOME_DIR = path
    return


class ConfigModel(object):

    @property
    def store_path(self) -> Path:
        return self._store_path

    @store_path.setter
    def store_path(self, new_val: Union[Path, str]):
        if type(new_val) is str:
            new_val = Path(new_val)
        self._validate_store_path(new_val)
        self._store_path = new_val
        return

    @property
    def editor(self) -> str:
        return self._editor

    @editor.setter
    def editor(self, new_val: str):
        self._validate_editor(new_val)
        self._editor = new_val
        return

    @property
    def hash_locker_names(self) -> bool:
        return self._hash_locker_names

    @hash_locker_names.setter
    def hash_locker_names(self, new_val: Union[bool, str]):
        if type(new_val) is str:
            new_val = new_val.lower() != "false"
        self._validate_hash_names(new_val)
        self._hash_locker_names = new_val
        return

    def __init__(
            self,
            store_path: Union[Path, str] = None,
            editor: str = None,
            hash_names: Union[bool, str] = None
    ):
        # Any of the args not passed in, get them from the environment
        self._store_path = store_path
        if store_path:
            # if it was passed in, use the property mutator (it validates)
            self.store_path = store_path
        else:
            self.store_path = environ.get("PHIBES_STORE_PATH", None)
        if editor:
            self.editor = editor
        else:
            self._editor = environ.get("PHIBES_EDITOR", None)
        if hash_names is not None:
            self.hash_locker_names = hash_names
        else:
            tmp_val = environ.get("PHIBES_HASH_LOCKER_NAMES", None)
            if tmp_val == "FALSE":
                self._hash_locker_names = False
            else:
                self._hash_locker_names = True
        self.apply()
        return

    def __str__(self):
        # Some things are not json serializable, e.g. Path
        ret_val = {
            "store_path": str(self.store_path.resolve()),
            "editor": self.editor,
            "hash_locker_names": self.hash_locker_names
        }
        return json.dumps(ret_val, indent=4)

    @staticmethod
    def _validate_store_path(val: Path):
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

    @staticmethod
    def _validate_editor(val):
        if type(val) is not str:
            raise PhibesConfigurationError(
                f"editor must be str, {val} is {type(val)}"
            )
        return

    @staticmethod
    def _validate_hash_names(val):
        if type(val) is not bool:
            raise PhibesConfigurationError(
                f"hash_locker_names must be bool, {val} is {type(val)}"
            )
        return

    def validate(self):
        failures = []
        # Trigger the field validation in each property mutator
        try:
            self.store_path = self._store_path
        except TypeError as err:
            failures.append(f"{err}\n")
        try:
            self.editor = self._editor
        except TypeError as err:
            failures.append(f"{err}\n")
        try:
            self.hash_locker_names = self._hash_locker_names
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
        environ['PHIBES_STORE_PATH'] = f"{self._store_path}"
        environ['PHIBES_EDITOR'] = f"{self._editor}"
        if self._hash_locker_names:
            environ['PHIBES_HASH_LOCKER_NAMES'] = "TRUE"
        else:
            environ['PHIBES_HASH_LOCKER_NAMES'] = "FALSE"


def set_editor(editor: str):
    """
    Set the editor in the current environment.
    Does not write to a file.
    """
    model = ConfigModel()
    model.editor = editor
    model.apply()


def load_config_file(path):
    """
    Read a config path and set the environment from it.
    """
    if not path.exists():
        raise FileNotFoundError(f"{path.absolute()} not found")
    if path.is_dir():
        conf_file = path.joinpath(CONFIG_FILE_NAME)
    elif path.is_file():
        conf_file = path
    else:
        raise ValueError(
            f"{path} must be an existing directory or a file"
        )
    with conf_file.open('r') as cf:
        conf_dict = json.loads(cf.read())
    conf_mod = ConfigModel(
        conf_dict['store_path'],
        conf_dict['editor'],
        conf_dict['hash_locker_names']
    )
    conf_mod.apply()
    return conf_mod


def write_config_file(path, config_model=None, update=False):
    """
    Write a config to a path
    With no config_model, write the values currently in the environment
    """
    if config_model is None:
        config_model = ConfigModel()
    config_model.validate()
    if path.exists():
        if path.is_dir():
            conf_file = path.joinpath(CONFIG_FILE_NAME)
        elif path.is_file():
            conf_file = path
        else:
            raise TypeError(
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
