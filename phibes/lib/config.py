"""
Package configuration
"""


# Built-in library packages
import getpass
import json
from os import environ
from pathlib import Path
import shutil
from typing import Union

# Third party packages
from colorama import init as color_init
from colorama import Fore, Style

# In-project modules
# Do not do that here. This is a 'leaf' module.

# TODO: provide server config, this is mostly single user, local CLI config

log = print

CONFIG_FILE_NAME = '.phibes.cfg'
HOME_DIR = None


def get_home_dir() -> Path:
    """
    This allows changing the home dir without changing the command
    interface. It simplifies configuring testing to not his user's home.
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

    storage_folder = '.phibes'
    default_storage_path = None
    default_editor = environ.get('EDITOR', 'unknown')
    default_hash_locker_names = True

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
            raise ValueError(
                f"store_path must be a Path, {val} is {type(val)}"
            )
        if not val.exists():
            try:
                val.mkdir()
            except FileNotFoundError:
                raise FileNotFoundError(
                    f"store_path {val} does not exist"
                )
        return

    @staticmethod
    def _validate_editor(val):
        if type(val) is not str:
            raise ValueError(
                f"editor must be str, {val} is {type(val)}"
            )
        return

    @staticmethod
    def _validate_hash_names(val):
        if type(val) is not bool:
            raise ValueError(
                f"hash_locker_names must be bool, {val} is {type(val)}"
            )
        return

    def validate(self):
        failures = []
        # Trigger the field validation in each property mutator
        try:
            self.store_path = self._store_path
        except ValueError as err:
            failures.append(f"{err}\n")
        try:
            self.editor = self._editor
        except ValueError as err:
            failures.append(f"{err}\n")
        try:
            self.hash_locker_names = self._hash_locker_names
        except ValueError as err:
            failures.append(f"{err}\n")
        if failures:
            raise ValueError(failures)
        return True

    def apply(self):
        self.validate()
        environ['PHIBES_STORE_PATH'] = f"{self._store_path}"
        environ['PHIBES_EDITOR'] = f"{self._editor}"
        if self._hash_locker_names:
            environ['PHIBES_HASH_LOCKER_NAMES'] = "TRUE"
        else:
            environ['PHIBES_HASH_LOCKER_NAMES'] = "FALSE"


def set_editor(editor: str):
    model = ConfigModel()
    model.editor = editor
    model.apply()


# class ConfigFile(object):
#
#     default_file_name = '.phibes.cfg'
#     default_config_path = get_home_dir().joinpath(default_file_name)
#
#     def __init__(self, filepath: Path):
#         self.filepath = filepath
#         return
#
#     def read(self):
#         """
#         Read config from file
#         :return:
#         """
#         if not self.filepath.exists():
#             raise FileNotFoundError(f"{self.filepath.absolute()} not found")
#         if self.filepath.is_dir():
#             conf_file = self.filepath.joinpath(self.default_file_name)
#         elif self.filepath.is_file():
#             conf_file = self.filepath
#         else:
#             raise ValueError(
#                 f"{self.filepath} must be an existing directory or a file"
#             )
#         with conf_file.open('r') as cf:
#             conf_dict = json.loads(cf.read())
#         conf_mod = ConfigModel(
#             conf_dict['store_path'],
#             conf_dict['editor'],
#             conf_dict['hash_locker_names']
#         )
#         conf_mod.validate()
#         return conf_mod
#
#     def write(self, config_model: ConfigModel):
#         config_model.validate()
#         if self.filepath.exists():
#             if self.filepath.is_dir():
#                 conf_file = self.filepath.joinpath(self.default_file_name)
#             elif self.filepath.is_file():
#                 conf_file = self.filepath
#             else:
#                 raise ValueError(
#                     f"{self.filepath} must be a directory or a file"
#                 )
#         else:
#             # don't try to figure it out, just try to write it
#             conf_file = self.filepath
#         try:
#             # print(f"writing to file {config_model}")
#             conf_file.write_text(f"{config_model}")
#         except FileNotFoundError:
#             raise
#         return
#
#     @classmethod
#     def write_config(cls, pth, **entries):
#         with Path(pth).joinpath(ConfigFile.default_file_name) as cf:
#             cf.write_text(json.dumps(entries, indent=4))
#         return
#

def load_config_file(path):
    # read a config path and set the environment from it
    # ConfigFile(path).read().apply()
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


def write_config_file(path, config_model=None):
    # write a config to a path
    if config_model is None:
        config_model = ConfigModel()
    config_model.validate()
    if path.exists():
        if path.is_dir():
            conf_file = path.joinpath(CONFIG_FILE_NAME)
        elif path.is_file():
            conf_file = path
        else:
            raise ValueError(
                f"{path} must be a directory or a file"
            )
    else:
        # don't try to figure it out, just try to write it
        conf_file = path
    try:
        # print(f"writing to file {config_model}")
        conf_file.write_text(f"{config_model}")
    except FileNotFoundError:
        raise
    return


# class Config(object):
#
#     file_name = '.phibes.conf'
#     storage_folder = '.phibes'
#     default_config_path = Path.home().joinpath(file_name)
#     default_storage_path = Path.home().joinpath(storage_folder)
#     default_editor = environ.get('EDITOR', 'unknown')
#     default_hash_locker_names = True
#     required_properties = ['hash_locker_names', 'store_path', 'editor']
#
#     @property
#     def hash_locker_names(self) -> bool:
#         return self._hash_locker_names
#
#     @hash_locker_names.setter
#     def hash_locker_names(self, new_val: Union[bool, str]):
#         if type(new_val) is not bool:
#             raise ValueError(
#                 f"new_val must be bool, {new_val} is {type(new_val)}"
#             )
#         self._hash_locker_names = new_val
#         return
#
#     @property
#     def store_path(self) -> Path:
#         return self._store_path
#
#     @store_path.setter
#     def store_path(self, new_val: Path):
#         if not isinstance(new_val, Path):
#             raise ValueError(
#                 f"new_val must be Path, {new_val} is {type(new_val)}"
#             )
#         self._store_path = new_val
#         return
#
#     @property
#     def users_path(self) -> Path:
#         return self.store_path.joinpath('users')
#
#     @property
#     def editor(self) -> str:
#         """
#         A config can be loaded from file that doesn't specify an editor,
#         and that will be fine as long as one of the environment vars is set
#         """
#         ret_val = environ.get(
#             'PHIBES_EDITOR', environ.get('EDITOR', self._editor)
#         )
#         if ret_val is None:
#             raise ValueError
#         return ret_val
#
#     @editor.setter
#     def editor(self, new_val: str):
#         if type(new_val) is not str:
#             raise ValueError(
#                 f"new_val must be str, {new_val} is {type(new_val)}"
#             )
#         self._editor = new_val
#         return
#
#     @classmethod
#     def write_config(cls, pth, **entries):
#         with Path(pth).joinpath(Config.file_name) as cf:
#             cf.write_text(json.dumps(entries, indent=4))
#         return
#
#     def __init__(self, conf_file_path=None):
#
#         def set_from_file(file_path: Path, required: list, optional: list):
#             """
#             Updates member variables from file
#             Does not attempt to revert if there is a failure, should
#             only live inside __init__ where values haven't otherwise been set.
#
#             :param file_path:
#             :param required: Tags that must be set or raise an exception
#             :param optional: Tags that may be set
#             :return:
#             """
#             if not file_path.exists():
#                 raise FileNotFoundError(f"{file_path.absolute()} not found")
#             if file_path.is_dir():
#                 file_path = file_path.joinpath(Config.file_name)
#             elif file_path.is_file():
#                 file_path = file_path
#             else:
#                 raise ValueError("That is not a good Path object")
#             with file_path.open('r') as cf:
#                 conf_dict = json.loads(cf.read())
#             missing_keys = set(required) - set(conf_dict.keys())
#             if missing_keys:
#                 raise ValueError(f"{file_path} missing {missing_keys}")
#             failed = False
#             # try to apply values by assignment in case fields have validation
#             msg = ''
#             if 'editor' in required:
#                 try:
#                     self.editor = conf_dict.get('editor')
#                 except Exception as err:
#                     failed = True
#                     msg += f"{err}\n"
#             if 'hash_locker_names' in required:
#                 if 'hash_locker_names' in conf_dict:
#                     temp_val = conf_dict.get('hash_locker_names')
#                     if type(temp_val) is str:
#                         self.hash_locker_names = temp_val.lower() not in [
#                             "false", "f"
#                         ]
#                 else:
#                     failed = True
#                     msg += f"hash_locker_names missing\n"
#             if 'store_path' in required:
#                 try:
#                     self.store_path = Path(conf_dict.get('store_path'))
#                 except Exception as err:
#                     failed = True
#                     msg += f"{err}\n"
#             if failed:
#                 raise ValueError(f"{msg}")
#             # editor may be optional as an override of the env $EDITOR
#             if 'editor' in optional:
#                 try:
#                     self.editor = conf_dict.get('editor')
#                 except Exception:
#                     pass
#             return
#
#         self._editor = None
#         self._hash_locker_names = None
#         self._store_path = None
#         tags_needed = []
#         tags_opts = []
#         if 'PHIBES_EDITOR' in environ:
#             self.editor = environ.get('PHIBES_EDITOR')
#         else:
#             if 'EDITOR' in environ:
#                 self.editor = environ.get('EDITOR')
#                 tags_opts.append('editor')
#             else:
#                 tags_needed.append('editor')
#
#         self._hash_locker_names = environ.get('PHIBES_HASH_LOCKER_NAMES', None)
#         if not self._hash_locker_names:
#             tags_needed.append('hash_locker_names')
#         self._store_path = environ.get('PHIBES_STORE_PATH', None)
#         if not self.store_path:
#             tags_needed.append('store_path')
#
#         if conf_file_path:
#             pref_file = Path(conf_file_path)
#             if pref_file.is_dir():
#                 pref_file = pref_file.joinpath(Config.file_name)
#             try:
#                 set_from_file(pref_file, tags_needed, tags_opts)
#                 self.path = pref_file
#             except Exception as err:
#                 print(f"{err}")
#                 raise err
#         else:
#             cwd_file = Path(conf_file_path).joinpath(Config.file_name)
#             set_from_file(cwd_file, tags_needed, tags_opts)
#             self.path = cwd_file
#         self.validate()
#         return
#
#     def assure_users_dir(self):
#         if self.users_path.exists():
#             if not self.users_path.is_dir():
#                 raise FileExistsError(
#                     f"{self.users_path} exists but is not a directory!"
#                 )
#         else:
#             self.users_path.mkdir()
#
#     def validate(self):
#         """
#         As long as each property is available, we have a valid runtime config
#         """
#         missing = []
#         for prop in self.required_properties:
#             try:
#                 getattr(self, prop)
#             except ValueError:
#                 missing.append(f"{prop}")
#         if missing:
#             raise ValueError(f"missing config properties: {missing}")
#         return
#
#     def __str__(self):
#         return (
#             f"path: {self.path.absolute()}\n"
#             f"editor: {self.editor}\n"
#             f"store_path: {self.store_path.absolute()}\n"
#             f"hash_locker_names: {self.hash_locker_names}\n"
#         )


# def system_remove():
#     """
#     Remove all application-wide data, presumably to perform a clean install.
#     Note: Does NOT remove any user Lockers.
#     To remove user Lockers, prefer to use the Locker API, or
#     filesystem operations outside of the application.
#     :return:
#     """
#     shutil.rmtree(get_config_item("SYSTEM_PATH"))
#     return


# def system_install(path):
#     """
#     Create filesystem scaffolding for the application.
#     Requires no "system" be present.
#     Will not disturb existing user files.
#     :return:
#     """
#     syspath = get_config_item("SYSTEM_PATH")
#     msg = f"installing at {syspath} instead of requested {path}"
#     print(msg)
#     if syspath.exists():
#         raise FileExistsError(
#             f"User must fully remove previous installation at {syspath}."
#         )
#     else:
#         syspath.mkdir()
#     # TODO: copy items that are part of the distribution e.g. templates
#     return


# def init_config(self):
#     """ Initializes the config (will wipe-out anything there)"""
#     color_init()
#     print(f"{Style.RESET_ALL}{Style.BRIGHT}Initial configuration")
#     print(f"{Style.RESET_ALL}Please enter your desired settings,")
#     print("defaults are in square brackets\n")
#     print(f"{Style.BRIGHT}{Fore.GREEN} + Directory:")
#     conf_dir = Path.home().joinpath('.ppp')
#     user_path = f"{Style.RESET_ALL}[{Style.DIM}{conf_dir}{Style.RESET_ALL}]"
#     if user_path == '':
#         user_path = conf_dir
#     print(f"\n{Style.BRIGHT}{Style.GREEN}Editor, blank for env $EDITOR:")
#     editor = input(f"{Style.RESET_ALL}[] ")
#     self.cfg['ppp'] = {}
#     self.cfg['ppp']['editor'] = editor
#     with open(self.torgo_cfg, 'w') as f:
#         self.cfg.write(f)
