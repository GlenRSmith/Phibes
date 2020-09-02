"""
EmptyLocker class used by several tests for setup, teardown
"""

# Standard library imports

# Related third party imports

# Local application/library specific imports
from phibes.lib.config import CONFIG_FILE_NAME
from phibes.lib.config import ConfigModel, set_home_dir
from phibes.lib.config import load_config_file, write_config_file
from phibes.lib.errors import PhibesNotFoundError
from phibes.lib.locker import Locker
from phibes.model import Item


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

    def update_config(self, config: ConfigModel):
        write_config_file(self.test_path, config, update=True)
        load_config_file(self.test_path)


class EmptyLocker(ConfigLoadingTestClass):

    my_locker = None
    locker_name = "my_locker"
    password = "StaplerRadioPersonWomanMan"

    def custom_setup(self, tmp_path):
        super(EmptyLocker, self).custom_setup(tmp_path)
        try:
            if Locker(self.locker_name, self.password):
                Locker.delete(self.locker_name, self.password)
        except PhibesNotFoundError:
            pass
        finally:
            self.my_locker = Locker(
                self.locker_name, self.password, create=True
            )
        return

    def custom_teardown(self, tmp_path):
        super(EmptyLocker, self).custom_teardown(tmp_path)
        Locker.delete(self.locker_name, self.password)
        return


class PopulatedLocker(EmptyLocker):

    def custom_setup(self, tmp_path):
        super(PopulatedLocker, self).custom_setup(tmp_path)
        for item_type in self.my_locker.registered_items.keys():
            content = (
                f"here is some stuff\n"
                f"password: HardHat\n"
                f"{item_type}:{item_type}_name\n"
            )
            pth = self.my_locker.get_item_path(
                f"{item_type}", f"{item_type}_name"
            )
            new_item = Item(
                self.my_locker.crypt_impl,
                f"{item_type}_name"
            )
            new_item.content = content
            new_item.save(pth)
        return

    def custom_teardown(self, tmp_path):
        super(PopulatedLocker, self).custom_teardown(tmp_path)
        return
