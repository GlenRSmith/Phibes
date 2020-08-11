"""
Package configuration
"""

# Built-in library packages
import json
from os import environ
from pathlib import Path
import shutil

# Third party packages
from colorama import init as color_init
from colorama import Fore, Style

# In-project modules
# Do not do that here. This is a 'leaf' module.

# TODO: provide server config, this is mostly single user, local CLI config

# Allow the user to configure an editor
# _EDITOR = None
# Allow the user to select the path where storage will be
# _STORE_PATH = None
# Allow the user to configure whether locker names are hashed on disk.
# Enabling this option makes it impossible to discover locker names.
# _HASH_LOCKER_NAME = True

# _CONFIG = {"BASE_PATH": Path('.')}
# _CONFIG = {"BASE_PATH": Path.home()}
# _CONFIG["SYSTEM_PATH"] = _CONFIG.get("BASE_PATH").joinpath("system")
# _CONFIG["USERS_PATH"] = _CONFIG.get("BASE_PATH").joinpath("users")
# Whether locker names in this instance are hashed (for security)
# _CONFIG["HASH_LOCKER_NAMES"] = True

log = print


class Config(object):

    file_name = 'phibes-config.json'

    @property
    def hash_locker_names(self) -> bool:
        return self._hash_locker_names

    @hash_locker_names.setter
    def hash_locker_names(self, new_val: bool):
        if type(new_val) is not bool:
            raise ValueError(
                f"new_val must be bool, {new_val} is {type(new_val)}"
            )
        self._hash_locker_names = new_val
        return

    @property
    def store_path(self) -> Path:
        return self._store_path

    @store_path.setter
    def store_path(self, new_val: Path):
        if not isinstance(new_val, Path):
            raise ValueError(
                f"new_val must be Path, {new_val} is {type(new_val)}"
            )
        self._store_path = new_val
        return

    @property
    def users_path(self) -> Path:
        return self.store_path.joinpath('users')

    @property
    def editor(self) -> str:
        return self._editor

    @editor.setter
    def editor(self, new_val: str):
        if type(new_val) is not str:
            raise ValueError(
                f"new_val must be str, {new_val} is {type(new_val)}"
            )
        self._editor = new_val
        return

    @classmethod
    def write_config(cls, pth, **entries):
        with Path(pth).joinpath(Config.file_name) as cf:
            cf.write_text(json.dumps(entries, indent=4))
        return

    def __init__(self, conf_file_path):

        # order of priority of configuration files:
        # 1a - user param `conf_file_path`
        # 1b - current working directory
        # 2b - user home directory
        # if a config file can be combined with environment variables,
        # additional config file will not be sought.
        # Config values will never be used from multiple config files.

        # order of priority of editor:
        # 1 - 'PP_EDITOR' environment variable
        # 2 - configuration file (see separate priority list)
        # 3 - 'EDITOR' environment variable

        def set_from_file(file_path: Path, required: list, optional: list):
            """
            Updates member variables from file
            Does not attempt to revert if there is a failure, should
            only live inside __init__ where values haven't otherwise been set.

            :param file_path:
            :param required: Tags that must be set or raise an exception
            :param optional: Tags that may be set
            :return:
            """
            if not file_path.exists():
                raise FileNotFoundError(f"{file_path.absolute()} not found")
            with file_path.open('r') as cf:
                conf_dict = json.loads(cf.read())
            missing_keys = set(required) - set(conf_dict.keys())
            if missing_keys:
                raise ValueError(f"{file_path} missing {missing_keys}")
            failed = False
            # try to apply values by assignment in case fields have validation
            msg = ''
            if 'editor' in required:
                try:
                    self.editor = conf_dict.get('editor')
                except Exception as err:
                    failed = True
                    msg += f"{err}\n"
            if 'hash_locker_names' in required:
                if 'hash_locker_names' in conf_dict:
                    temp_val = conf_dict.get('hash_locker_names')
                    if type(temp_val) is str:
                        self.hash_locker_names = temp_val.lower() not in ["false", "f"]
                else:
                    failed = True
                    msg += f"hash_locker_names missing\n"
            if 'store_path' in required:
                try:
                    self.store_path = Path(conf_dict.get('store_path'))
                except Exception as err:
                    failed = True
                    msg += f"{err}\n"
            if failed:
                raise ValueError(f"{msg}")
            # editor may be optional as an override of the env $EDITOR
            if 'editor' in optional:
                try:
                    self.editor = conf_dict.get('editor')
                except Exception:
                    pass
            return

        self._editor = None
        self._hash_locker_names = None
        self._store_path = None
        tags_needed = []
        tags_opts = []
        if 'PP_EDITOR' in environ:
            self.editor = environ.get('PP_EDITOR')
        else:
            if 'EDITOR' in environ:
                self.editor = environ.get('EDITOR')
                tags_opts.append('editor')
            else:
                tags_needed.append('editor')

        self._hash_locker_names = environ.get('PP_HASH_LOCKER_NAMES', None)
        if not self._hash_locker_names:
            tags_needed.append('hash_locker_names')
        self._store_path = environ.get('PP_STORE_PATH', None)
        if not self.store_path:
            tags_needed.append('store_path')

        if conf_file_path:
            pref_file = Path(conf_file_path)
            if pref_file.is_dir():
                pref_file = pref_file.joinpath(Config.file_name)
            try:
                set_from_file(pref_file, tags_needed, tags_opts)
                self.path = pref_file
            except Exception as err:
                print(f"{err}")
                raise err
        else:
            # cwd_file = Path.cwd().joinpath(Config.file_name)
            cwd_file = Path(conf_file_path).joinpath(Config.file_name)
            # try:
            # import os
            # raise ValueError(f"{cwd_file.absolute()}\n{os.getcwd()}")

            set_from_file(cwd_file, tags_needed, tags_opts)
            # set_from_file(cwd_file, tags_needed, tags_opts)
            self.path = cwd_file
            # except Exception as err:
            #     print(f"{err}")
            #     user_file = Path.home().joinpath(self.file_name)
            #     set_from_file(user_file, tags_needed, tags_opts)
            #     self.path = user_file

        # warnings = ""
        # self.path = None
        # if not self.path:
        #     msg = f"warnings: {warnings}"
        #     raise ValueError(msg)
        # elif warnings:
        #     print(f"warnings: {warnings}")
        return

    def assure_users_dir(self):
        if self.users_path.exists():
            if not self.users_path.is_dir():
                raise FileExistsError(
                    f"{self.users_path} exists but is not a directory!"
                )
        else:
            self.users_path.mkdir()

    def __str__(self):
        return (
            f"path: {self.path.absolute()}\n"
            f"editor: {self.editor}\n"
            f"store_path: {self.store_path.absolute()}\n"
            f"hash_locker_names: {self.hash_locker_names}\n"
        )


def system_remove():
    """
    Remove all application-wide data, presumably to perform a clean install.
    Note: Does NOT remove any user Lockers.
    To remove user Lockers, prefer to use the Locker API, or
    filesystem operations outside of the application.
    :return:
    """
    shutil.rmtree(get_config_item("SYSTEM_PATH"))
    return


def system_install(path):
    """
    Create filesystem scaffolding for the application.
    Requires no "system" be present.
    Will not disturb existing user files.
    :return:
    """
    syspath = get_config_item("SYSTEM_PATH")
    msg = f"installing at {syspath} instead of requested {path}"
    print(msg)
    if syspath.exists():
        raise FileExistsError(
            f"User must fully remove previous installation at {syspath}."
        )
    else:
        syspath.mkdir()
    assure_users_dir()
    # TODO: copy items that are part of the distribution e.g. templates
    return


# def get_config_item(item):
#     return _CONFIG.get(item, None)
#
#
# def get_system_path():
#     return get_config_item("SYSTEM_PATH")
#
#

def init_config(self):
    """ Initializes the config (will wipe-out anything there)"""
    color_init()
    print(f"{Style.RESET_ALL}{Style.BRIGHT}Initial configuration")
    print(f"{Style.RESET_ALL}Please enter your desired settings,")
    print("defaults are in square brackets\n")
    print(f"{Style.BRIGHT}{Fore.GREEN} + Directory:")
    conf_dir = Path.home().joinpath('.ppp')
    user_path = f"{Style.RESET_ALL}[{Style.DIM}{conf_dir}{Style.RESET_ALL}]"
    if user_path == '':
        user_path = conf_dir
    print(f"\n{Style.BRIGHT}{Style.GREEN}Editor, blank for env $EDITOR:")
    editor = input(f"{Style.RESET_ALL}[] ")
    self.cfg['ppp'] = {}
    self.cfg['ppp']['editor'] = editor
    with open(self.torgo_cfg, 'w') as f:
        self.cfg.write(f)
