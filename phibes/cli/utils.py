"""
Command-line interface to python privacy playground features
"""

# core library modules
import os
import sys

# third party packages
import click
from colorama import Fore, Style
# for purposes of the CLI project, lib is being treated as third-party!
from lib import config
from lib.item import Item
from lib.locker import Locker
from lib.secret import Secret

# local project modules


