"""
Various helpful bits
"""

# core library modules
import os

# third party packages

# local project modules
from lib.config import get_user_editor, USER_EDIT_FILE


def get_user_edit_content():
    editor = get_user_editor()
    os.system(f"{editor} {USER_EDIT_FILE}")
    with open(USER_EDIT_FILE, "r") as user_file:
        ret_val = user_file.read()
    os.remove(USER_EDIT_FILE)
    return ret_val


def write_user_edit_content(text):
    with open(USER_EDIT_FILE, "w") as user_file:
        user_file.write(text)
