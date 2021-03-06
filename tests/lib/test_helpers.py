"""
Module for various bits used in testing, such as
Base test classes used by several tests for setup, teardown
"""

# Standard library imports
import itertools
import random
from typing import Dict

# Related third party imports

# Local application/library specific imports
from phibes import crypto
from phibes.cli.cli_config import CLI_CONFIG_FILE_NAME, set_home_dir
from phibes.lib.config import ConfigModel
from phibes.lib.config import load_config_file, write_config_file
from phibes.lib.config import StoreType
from phibes.lib.errors import PhibesNotFoundError
from phibes.model import Locker


plain_texts = [
    "Easy Peasy",
    "this is my password for bouncycastledelivery.com",
    "this is my password \t for bouncycastledelivery.com",
    "this is my password \n for bouncycastledelivery.com",
    "This is just a test 1",
    "That is just a test 2",
    "We were just a test 3",
    "They will just be a test 4",
    """
    site:www.bouncycastledelivery.com
    username:Jenny'sMomAndDad
    password:WeWantToThrowtheb3stbirthdayparty07
    """,
    """
    {
        'site':'www.bouncycastledelivery.com',
        'username':'Jenny'sMomAndDad',
        'password':'WeWantToThrowtheb3stbirthdayparty07'
    }
    """
]


class ParametrizeArgs(object):
    def __init__(self, params: Dict):
        """
        Takes a dict of param name:list of values,
        Builds a `names` property: comma-separated list of names, and
        Builds a list of tuples with all combinations of param values
        """
        self.names = ','.join(params.keys())
        self.params = [i for i in itertools.product(*params.values())]


class BaseTestClass(object):

    test_path = None

    def custom_setup(self, tmp_path):
        self.test_path = tmp_path
        return

    def custom_teardown(self, tmp_path):
        return


class ConfigLoadingTestClass(BaseTestClass):

    editor = "vim"

    def custom_setup(self, tmp_path):
        super(ConfigLoadingTestClass, self).custom_setup(tmp_path)
        set_home_dir(tmp_path)
        conf = ConfigModel(
            store={
                'store_type': StoreType.FileSystem.name,
                'store_path': tmp_path
            },
            store_path=tmp_path
        )
        conf.apply()
        write_config_file(tmp_path, conf)
        self.test_path = tmp_path
        load_config_file(tmp_path)
        return

    def custom_teardown(self, tmp_path):
        conf = tmp_path / CLI_CONFIG_FILE_NAME
        # conf.unlink()
        return

    def update_config(self, config: ConfigModel) -> ConfigModel:
        write_config_file(self.test_path, config, update=True)
        return load_config_file(self.test_path)


class EmptyLocker(ConfigLoadingTestClass):

    my_locker = None
    locker_name = "my_locker"
    password = "StaplerRadioPersonWomanMan"
    lockers = {}

    def custom_setup(self, tmp_path):
        super(EmptyLocker, self).custom_setup(tmp_path)
        for name in self.lockers:
            try:
                Locker.delete(name, self.password)
            except PhibesNotFoundError:
                pass
        self.lockers = {}
        try:
            Locker.delete(self.locker_name, self.password)
        except PhibesNotFoundError:
            pass
        finally:
            self.my_locker = Locker.create(
                password=self.password,
                crypt_id=crypto.default_id,
                locker_name=self.locker_name
            )
            # create a locker for each registered crypt instance
            for crypt_id in crypto.list_crypts():
                # dedupe the names with random numbers
                wart = str(random.randint(1000, 9999))
                # but make sure there isn't a freak collision
                while self.locker_name + str(wart) in self.lockers:
                    wart = str(random.randint(1000, 9999))
                locker_name = self.locker_name + wart
                self.lockers[locker_name] = Locker.create(
                    password=self.password,
                    crypt_id=crypt_id,
                    locker_name=locker_name
                )
        return

    def custom_teardown(self, tmp_path):
        super(EmptyLocker, self).custom_teardown(tmp_path)
        return


class PopulatedLocker(EmptyLocker):

    common_item_name = "phibes_test_item"
    content = (
            f"here is some stuff\n"
            f"password: HardHat\n"
            f"some name\n"
        )

    def custom_setup(self, tmp_path):
        super(PopulatedLocker, self).custom_setup(tmp_path)
        all_lockers = list(self.lockers.values())
        all_lockers.append(self.my_locker)
        for lck in all_lockers:
            new_item = lck.create_item(
                item_name=self.common_item_name
            )
            new_item.content = self.content
            lck.add_item(item=new_item)
        return

    def custom_teardown(self, tmp_path):
        super(PopulatedLocker, self).custom_teardown(tmp_path)
        return
