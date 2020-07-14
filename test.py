#!/usr/bin/env python
"""
Tests for python privacy playground
"""

# core library modules
import shutil

# third party packages

# local project modules
from lib.locker import Locker
from lib.locker import Secret


def test_things():
    locker_name = "test_locker"
    locker_password = "LOLT3st1ng"
    new_locker = Locker(
        locker_name, locker_password, create=True
    )
    secret_name = "ponies.com"
    secret_text = "BatteryHorseStaplerCorrect"
    new_secret = Secret(secret_name, new_locker)
    new_secret.create(secret_text)

    old_locker = Locker(
        locker_name, locker_password, create=False
    )
    old_secret = Secret(secret_name, old_locker)
    read_pw = old_secret.read()
    assert secret_text == read_pw
    shutil.rmtree(old_locker.locker_path)
    return


if __name__ == '__main__':
    test_things()
