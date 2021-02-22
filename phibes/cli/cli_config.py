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


HOME_DIR = None
CLI_CONFIG_FILE_NAME = '.phibes_cli.cfg'
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


class CliConfig(object):
    """
    Configuration model class for command-line utility
    """
    @property
    def editor(self) -> str:
        """
        Accessor for configuration editor
        :return: protected _editor attribute
        """
        return environ.get('PHIBES_CLI_EDITOR', None)

    @editor.setter
    def editor(self, new_val: str):
        """
        Mutator for configured editor
        :param new_val: new editor to assign
        :return: None
        """
        self._validate_editor(new_val)
        self._editor = new_val
        environ['PHIBES_CLI_EDITOR'] = new_val

    @property
    def work_path(self) -> str:
        """
        Accessor for configuration work_path
        :return: protected _work_path attribute
        """
        ret_val = environ['PHIBES_CLI_WORK_PATH']
        return ret_val

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

    def __init__(self, editor: str = None, work_path: str = None):
        # Any of the args not passed in, get them from the environment
        if editor:
            self.editor = editor
        else:
            self._editor = environ.get("PHIBES_CLI_EDITOR", None)
        if work_path:
            self.work_path = work_path
        else:
            self._work_path = environ.get("PHIBES_CLI_WORK_PATH", None)
        self.apply()

    def __str__(self):
        """
        Override the string representation
        """
        # Some things are not json serializable, e.g. Path
        ret_val = {
            "editor": self.editor,
            "work_path": self.work_path
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
    conf_mod = CliConfig(conf_dict['editor'])
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