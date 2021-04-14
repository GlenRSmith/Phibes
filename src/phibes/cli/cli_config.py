"""
CLI environment configuration
"""

# Built-in library packages
import json
from os import environ
from pathlib import Path

# Third party packages
# In-project modules
from phibes.cli.errors import PhibesCliConfigurationError
from phibes.lib.config import ConfigModel, CONFIG_FILE_NAME
from phibes.lib.utils import todict


HOME_DIR = None
CLI_CONFIG_FILE_NAME = CONFIG_FILE_NAME
DEFAULT_EDITOR = environ.get('EDITOR', 'unknown')


def get_home_dir() -> Path:
    """
    Return the possibly over-ridden home directory
    """
    global HOME_DIR
    if not HOME_DIR:
        HOME_DIR = Path.home()
    return HOME_DIR


def set_home_dir(path: Path) -> None:
    """
    This allows changing the home dir without changing the command
    interface.
    It simplifies configuring testing to not use user's home directory.
    """
    global HOME_DIR
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    HOME_DIR = path
    return


class CliConfig(ConfigModel):
    """
    Configuration model class for command-line utility
    """
    @property
    def editor(self) -> str:
        """
        Accessor for configuration editor
        :return: protected _editor attribute
        """
        if self._editor is None:
            self._editor = environ.get('PHIBES_EDITOR', DEFAULT_EDITOR)
        return self._editor

    @editor.setter
    def editor(self, new_val: str):
        """
        Mutator for configured editor
        :param new_val: new editor to assign
        :return: None
        """
        self._validate_editor(new_val)
        self._editor = new_val
        environ['PHIBES_EDITOR'] = new_val

    @property
    def work_path(self) -> str:
        """
        Accessor for configuration work_path
        :return: protected _work_path attribute
        """
        if self._work_path is None:
            self._work_path = environ.get('PHIBES_CLI_WORK_PATH', None)
        return self._work_path

    @work_path.setter
    def work_path(self, new_val: str):
        """
        Mutator for configured work_path
        :param new_val: new work_path to assign
        :return: None
        """
        self._validate_work_path(new_val)
        self._work_path = new_val
        environ['PHIBES_CLI_WORK_PATH'] = new_val

    def __init__(self, **kwargs):
        """
        Create a config object
        @param editor:
        @param work_path:
        @param kwargs:
        """
        # IDE complains about instance attrs not explicitly set in __init__
        self._editor = None
        self._work_path = None
        required = []
        optional = ['editor', 'work_path']
        err_list = []
        for name in optional + required:
            arg_val = kwargs.get(name, None)
            try:
                self._set_private_property(
                    name=name, value=arg_val, optional=(name not in required)
                )
            except Exception as err:
                msg = f'exception setting private property {name=}'
                msg += f'exception setting private property {arg_val=}'
                msg += f'exception setting private property {err=}'
                err_list.append(msg)
        if err_list:
            raise PhibesCliConfigurationError(
                f'missing required arg(s): {err_list}'
            )
        if 'store_path' in kwargs:
            self.store = {
                'store_type': 'FileSystem',
                'store_path': kwargs['store_path']
            }
        super(CliConfig, self).__init__(**kwargs)
        self.apply()

    def __str__(self):
        """
        Override the string representation
        """
        # Some things are not json serializable, e.g. Path
        # ret_val = todict(self)
        try:
            ret_val = todict(self)
        except Exception as err:
            if not self.work_path:
                wp = '-'
            else:
                wp = self.work_path
            ret_val = {
                "todict result": f'{err}',
                "exception type": f'{type(err)}',
                "self.__dict__": f'{self.__dict__}',
                "editor": self.editor,
                "work_path": wp,
                "store": str(self.store)
            }
        return json.dumps(ret_val, indent=4)

    @staticmethod
    def _validate_editor(val):
        if type(val) is not str:
            raise PhibesCliConfigurationError(
                f"editor must be str, {val} is {type(val)}"
            )
        return

    @staticmethod
    def _validate_work_path(val):
        if type(val) is not str:
            raise PhibesCliConfigurationError(
                f"work_path must be str, {val} is {type(val)}"
            )
        return

    def validate(self):
        failures = []
        # Trigger the field validation in each property mutator
        if self._editor is not None:
            try:
                self.editor = self._editor
            except TypeError as err:
                failures.append(f"{err}\n")
        if self._work_path is not None:
            try:
                self.work_path = self._work_path
            except TypeError as err:
                failures.append(f"{err}\n")
        if failures:
            raise PhibesCliConfigurationError(failures)
        return True

    def apply(self):
        """
        Make the values in this instance the "live" config
        """
        self.validate()


def load_config_file(path):
    """
    Read a config path and set the environment from it.
    """
    if not path.exists():
        raise FileNotFoundError(f"{path.absolute()} not found")
    if path.is_dir():
        conf_file = path.joinpath(CLI_CONFIG_FILE_NAME)
    elif path.is_file():
        conf_file = path
    else:
        raise ValueError(
            f"{path} must be an existing directory or a file"
        )
    with conf_file.open('r') as cf:
        conf_dict = json.loads(cf.read())
    conf_mod = CliConfig(editor=conf_dict['editor'])
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
        config_model = CliConfig()
    if not bypass_validation:
        config_model.validate()
    if path.exists():
        if path.is_dir():
            conf_file = path.joinpath(CLI_CONFIG_FILE_NAME)
        elif path.is_file():
            conf_file = path
        else:
            raise TypeError(
                f"{path} must be a directory or a file"
            )
    elif path.name == CLI_CONFIG_FILE_NAME and path.parent.exists():
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
