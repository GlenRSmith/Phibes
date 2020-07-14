#!/usr/bin/env python
"""
Functions to replicate the LastPass model
"""

# standard library
import getpass

# third party libraries

# in-project modules
import locker


def mfa_auth():
    # placeholder for MFA auth of crypt
    # https://pypi.org/project/authenticator/
    return None


def demo_script():
    print("Create a new user account and crypt")
    username = input("Name: ")
    pass1 = getpass.getpass()
    pass2 = getpass.getpass()
    if pass1 != pass2:
        raise Exception("passwords don't match")
    new_locker = locker.Locker(
        username, pass1, create=True
    )
    print("User account created")
    print(f"{new_locker.auth_hash}")
    existing_locker = locker.Locker(username, pass2)
    hide = "BatteryHorseStaplerCorrect"
    print(f"hide: {hide}")
    iv, hidden = locker.encrypt(
        existing_locker.crypt_key,
        hide
    )
    print(f"existing_locker.crypt_key: {existing_locker.crypt_key}")
    print(f"existing_locker.crypt_key: {existing_locker.crypt_key.hex()}")
    print(f"encrypted form {hidden}")
    unhidden = locker.decrypt(
        existing_locker.crypt_key,
        iv,
        hidden
    ).decode()
    print(f"unhidden {unhidden}")
    assert hide == unhidden
    return


def main():
    demo_script()
    return


if __name__ == '__main__':
    main()
