"""
Various helpful bits
"""

# core library modules
import os
import sys

# third party packages

# local project modules
from lib.config import USER_EDIT_FILE


def get_user_edit_content(editor):
    # open a temp file in the user's editor
    # sys.exit(os.system('{0} {1}'.format(editor, str(USER_EDIT_FILE))))
    # open the file and read it entirely
    with open(USER_EDIT_FILE, "r") as user_file:
        ret_val = user_file.read()
    # os.remove(USER_EDIT_FILE)
    return ret_val
