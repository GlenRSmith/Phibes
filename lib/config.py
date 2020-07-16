"""
Package configuration
"""

# Built-in library packages
import os

# Third party packages

# In-project modules
# Do not do that here. This is a 'leaf' module.

LOCKER_PATH = "locker"
USER_EDIT_PATH = os.path.join(LOCKER_PATH, 'tmp')
USER_EDIT_FILE = os.path.join(USER_EDIT_PATH, 'tmp.txt')
