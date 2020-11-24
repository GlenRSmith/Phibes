"""
EmptyLocker class used by several tests for setup, teardown
"""

# Standard library imports
import random

# Related third party imports

# Local application/library specific imports
from phibes.lib.config import CONFIG_FILE_NAME
from phibes.lib.config import ConfigModel, set_home_dir
from phibes.lib.config import load_config_file, write_config_file
from phibes import crypto
from phibes.lib.errors import PhibesNotFoundError
from phibes.model import Item, Locker


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


class BaseTestClass(object):

    test_path = None

    def custom_setup(self, tmp_path):
        self.test_path = tmp_path
        return

    def custom_teardown(self, tmp_path):
        return


class ConfigLoadingTestClass(BaseTestClass):

    editor = "vim"
    hash_locker_names = "False"

    def custom_setup(self, tmp_path):
        super(ConfigLoadingTestClass, self).custom_setup(tmp_path)
        set_home_dir(tmp_path)
        conf = ConfigModel(
            store_path=tmp_path,
            editor=self.editor,
            hash_names=self.hash_locker_names
        )
        write_config_file(tmp_path, conf)
        self.test_path = tmp_path
        load_config_file(tmp_path)
        return

    def custom_teardown(self, tmp_path):
        conf = tmp_path / CONFIG_FILE_NAME
        conf.unlink()
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
            self.my_locker = Locker.create(self.locker_name, self.password)
            # create a locker for each registered crypt instance
            for crypt_id in crypto.list_crypts():
                # dedupe the names with random numbers
                wart = str(random.randint(1000, 9999))
                # but make sure there isn't a freak collision
                while self.locker_name + str(wart) in self.lockers:
                    wart = str(random.randint(1000, 9999))
                name = self.locker_name + wart
                self.lockers[name] = Locker.create(
                    name, self.password, crypt_id
                )
        return

    def custom_teardown(self, tmp_path):
        super(EmptyLocker, self).custom_teardown(tmp_path)
        return


class PopulatedLocker(EmptyLocker):

    def custom_setup(self, tmp_path):
        super(PopulatedLocker, self).custom_setup(tmp_path)
        all_lockers = list(self.lockers.values())
        all_lockers.append(self.my_locker)
        content = (
            f"here is some stuff\n"
            f"password: HardHat\n"
            f"some name\n"
        )
        for lck in all_lockers:
            pth = lck.get_item_path("secret_name")
            new_item = Item(lck.crypt_impl, "secret_name")
            new_item.content = content
            new_item.save(pth)
        return

    def custom_teardown(self, tmp_path):
        super(PopulatedLocker, self).custom_teardown(tmp_path)
        return
