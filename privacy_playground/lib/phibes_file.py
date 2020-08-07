"""
PhibesFile provides read/write services for the uniform layout
that is shared by the locker file and all item files.

Line 1: the salt value (a hex string)
Line 2: the timestamp at the time the file was written
Line 3: the user content

This file interface is 'agnostic' about encryption,
but for complete reference, the standard is that Lines 2 & 3 are
encrypted.
"""

# Built-in library packages
from __future__ import annotations
from pathlib import Path

# Third party packages

# In-project modules


def read(pth: Path) -> dict:
    """
    Read the file at pth, return a dict with uniform keys
    :param pth:
    :return:
    """
    if not pth.exists():
        raise FileNotFoundError(
            f"Item file {pth} not found"
        )
    ret_val = dict()
    with pth.open('r') as cf:
        # the salt was stored as a hexadecimal string
        ret_val['salt'] = cf.readline().strip('\n')
        # the next line is an encrypted datetime stamp
        ret_val['timestamp'] = cf.readline().strip('\n')
        # the next line is the encrypted content
        ret_val['body'] = cf.readline().strip('\n')
    return ret_val


def write(
        pth: Path,
        salt: str,
        timestamp: str,
        body: str,
        overwrite: bool = False
) -> None:
    """
    Write the salt, timestamp, and body to the specified pth file
    :param pth: Path object to write
    :param salt: salt value
    :param timestamp: timestamp
    :param body: body
    :param overwrite: whether to overwrite an existing file
    :return: None
    """
    if pth.exists() and not overwrite:
        raise FileExistsError(
            f"file {pth} already exists, and overwrite is False"
        )
    if not body:
        raise AttributeError(f"Record has no content!")
    if "\n" in salt or "\n" in timestamp or "\n" in body:
        raise ValueError(
            f"File fields can not contain newline char\n"
            f"salt: {salt}"
            f"timestamp: {timestamp}"
            f"body: {body}"
        )
    with pth.open("w") as cipher_file:
        cipher_file.write(
            f"{salt}\n{timestamp}\n{body}\n"
        )
    return
