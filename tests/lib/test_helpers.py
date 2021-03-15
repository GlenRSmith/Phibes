"""
EmptyLocker class used by several tests for setup, teardown
"""

# Standard library imports
import random

# Related third party imports

# Local application/library specific imports
from phibes import crypto
from phibes.cli.cli_config import set_home_dir
from phibes.cli.commands import build_cli_app
from phibes.lib.config import CONFIG_FILE_NAME
from phibes.lib.config import ConfigModel
from phibes.lib.config import load_config_file, write_config_file
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
        conf = ConfigModel(store_path=tmp_path)
        write_config_file(tmp_path, conf)
        self.test_path = tmp_path
        load_config_file(tmp_path)
        return

    def custom_teardown(self, tmp_path):
        conf = tmp_path / CONFIG_FILE_NAME
        # conf.unlink()
        return

    def update_config(self, config: ConfigModel) -> ConfigModel:
        write_config_file(self.test_path, config, update=True)
        return load_config_file(self.test_path)


class BaseAnonLockerTest(ConfigLoadingTestClass):

    password = None
    command_name = None
    target = None
    action = None
    func = None
    click_group = None

    def custom_setup(self, tmp_path):
        super(BaseAnonLockerTest, self).custom_setup(tmp_path)
        build_cli_app(
            command_dict={
                self.target: {
                    self.action: {
                        'name': self.command_name,
                        'func': self.__class__.func
                    }
                }
            },
            click_group=self.click_group,
            named_locker=False
        )


class AnonLocker(ConfigLoadingTestClass):

    my_locker = None
    locker_name = None
    password = "78CollECtion!CampCoolio"

    def custom_setup(self, tmp_path):
        super(AnonLocker, self).custom_setup(tmp_path)
        try:
            Locker.delete(
                locker_name=self.locker_name,
                password=self.password
            )
        except PhibesNotFoundError:
            pass
        finally:
            self.my_locker = Locker.create(
                password=self.password,
                crypt_id=self.crypt_id,
                locker_name=self.locker_name
            )

    def custom_teardown(self, tmp_path):
        super(AnonLocker, self).custom_teardown(tmp_path)


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
            new_item = lck.create_item(item_name="secret_name")
            new_item.content = content
            lck.add_item(item=new_item)
        return

    def custom_teardown(self, tmp_path):
        super(PopulatedLocker, self).custom_teardown(tmp_path)
        return
