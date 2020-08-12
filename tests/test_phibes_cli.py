"""
pytest module for phibes
"""

# Standard library imports
# import shutil
import json

# Related third party imports

# Local application/library specific imports
from phibes.lib.config import Config


def copy_config(source, target):
    my_conf = source.read()
    Config.write_config(target, **json.loads(my_conf))
    return


# datadirs = [
#     ('tests.test_phibes/TestCreateLocker/test_create_locker'),
#     ('tests.test_phibes/TestCreateLocker'),
#     ('tests.test_phibes'),
#     ('data/tests.test_phibes/TestCreateLocker/test_create_locker'),
#     ('data/tests.test_phibes/TestCreateLocker'),
#     ('data/tests.test_phibes'),
#     ('data')
# ]


class TestEdit(object):

    def test_edit(self):
        return
