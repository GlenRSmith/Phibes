"""
pytest module for backward compatibility
"""

# Standard library imports
from pathlib import Path

# Related third party imports

# Local application/library specific imports
from phibes.crypto import list_crypts
from phibes.model import Locker
from phibes.lib.config import ConfigModel
from phibes.lib.config import load_config_file, write_config_file


plain_texts = {
    "thing1": "Easy Peasy",
    "thing2": "this is my password for bouncycastledelivery.com",
    "thing3": "this is my password \t for bouncycastledelivery.com",
    "thing4": "this is my password \n for bouncycastledelivery.com",
    "thing5": "This is just a test 1",
    "thing6": "That is just a test 2",
    "thing7": "We were just a test 3",
    "thing8": "They will just be a test 4",
    "thing9": """
            site:www.bouncycastledelivery.com
            username:Jenny'sMomAndDad
            password:WeWantToThrowtheb3stbirthdayparty07
        """,
    "thingA": """
        {
            'site':'www.bouncycastledelivery.com',
            'username':'Jenny'sMomAndDad',
            'password':'WeWantToThrowtheb3stbirthdayparty07'
        }
        """
}


def validate_locker(name, pw):
    lock = Locker.get(name, pw)
    assert len(lock.list_items()) == len(plain_texts)
    for name, pt in plain_texts.items():
        it = lock.get_item(name)
        content = (
            f"{pt}\nsite:www.zombo.com\npassword: YouCanD0NEthing!"
        )
        assert it.content == content
    return


def validate_install(installed_path, locker_name, pw):
    load_config_file(installed_path)
    # override stored "dummy" store_path with the current installed path
    ConfigModel(store_path=installed_path)
    validate_locker(locker_name, pw)
    return


class TestBackCompat:

    test_name = "test_locker"
    test_pw = "test_password"

    def test_validate_installs(self, datadir):
        # Get the list of install directories under `tests/data`
        data_root = datadir['.']
        installs = data_root.listdir()
        # Each directory is named for a crypt_id, representing an installation
        # Each installation has its own .phibes.cfg and one test locker
        installed_paths = set()
        crypt_dirs = set()
        for install in installs:
            installed_paths.add(Path(install))
            crypt_dirs.add(install.basename)
        # The directory listing should exactly match registered crypt_ids
        warnings = ""
        for item in set(list_crypts()) - crypt_dirs:
            warnings += f"Registered crypt {item} missing test install\n"
        for item in crypt_dirs - set(list_crypts()):
            warnings += f"No crypt registered matching test install {item}\n"
        assert not warnings
        for pt in installed_paths:
            validate_install(pt, self.test_name, self.test_pw)

    def _test_create_installs(self, datadir):
        """
        This is a bootstrap for one-time use creating lockers to be tested
        so we know nothing in our encryption has changed
        """
        for crypt_id in list_crypts():
            data_root = datadir['.']
            new_loc = Path(data_root/crypt_id)
            new_loc.mkdir()
            conf = ConfigModel(
                store_path=new_loc, editor='vim'
            )
            write_config_file(new_loc, conf)
            new_lock = Locker.create(self.test_name, self.test_pw, crypt_id)
            for name, pt in plain_texts.items():
                ni = new_lock.create_item(name)
                ni.content = (
                    f"{pt}\nsite:www.zombo.com\npassword: YouCanD0NEthing!"
                )
                new_lock.add_item(ni)
            # after lockers are stored, stub out the store_path
            conf._store_path = Path("/")
            write_config_file(
                new_loc, conf, update=True, bypass_validation=True
            )
