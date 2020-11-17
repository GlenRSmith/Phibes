"""
pytest module for backward compatibility
"""

# Standard library imports
from pathlib import Path

# Related third party imports

# Local application/library specific imports
from phibes.crypto import list_crypts
from phibes.model import Locker
from phibes.lib.config import ConfigModel, load_config_file, write_config_file


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


class TestBackCompat:

    test_name = "test_locker"
    test_pw = "test_password"
    test_item_type = "secret"

    def test_validate_installs(self, datadir):
        # Get the list of install directories under `tests/data`
        data_root = datadir['.']
        installs = data_root.listdir()
        # Each directory is named for a crypt_id, representing an installation
        # Each installation has its own .phibes.cfg and one test locker
        pts = set()
        nts = set()
        for install in installs:
            pts.add(Path(install))
            nts.add(install.basename)
        # The directory listing should exactly match registered crypt_ids
        assert set(list_crypts()) == nts
        for pt in pts:
            load_config_file(pt)
            lock = Locker.get(self.test_name, self.test_pw)
            for name, pt in plain_texts.items():
                it = lock.get_item(name, self.test_item_type)
                content = (
                    f"{pt}\nsite:www.zombo.com\npassword: YouCanD0NEthing!"
                )
                assert it.content == content

    def _test_create_installs(self, datadir):
        """
        This is a bootstrap for one-time use creating lockers to be tested
        so we know nothing in our encryption has changed
        """
        for crypt_id in list_crypts():
            data_root = datadir['.']
            new_loc = Path(data_root/crypt_id)
            new_loc.mkdir()
            write_config_file(
                new_loc,
                ConfigModel(
                    store_path=new_loc.resolve().as_posix(),
                    editor='vim',
                    hash_names=True
                )
            )
            new_lock = Locker.create(self.test_name, self.test_pw, crypt_id)
            for name, pt in plain_texts.items():
                ni = new_lock.create_item(name, self.test_item_type)
                ni.content = (
                    f"{pt}\nsite:www.zombo.com\npassword: YouCanD0NEthing!"
                )
                new_lock.add_item(ni)