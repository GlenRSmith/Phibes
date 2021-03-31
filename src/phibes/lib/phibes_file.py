"""
PhibesFile provides read/write services for the uniform layout
that is shared by the locker file and all item files.

Line 1: the salt value (a hex string)
Line 2: the unique ID of the crypt handler
Line 3: the timestamp at the time the file was written
Line 4: the user content

This file interface is 'agnostic' about encryption,
but for complete reference, the standard is that Lines 4 is
encrypted.
"""

# Built-in library packages
from __future__ import annotations
from pathlib import Path

# Third party packages

# In-project modules


def read(pth: Path) -> dict:
    """
    Read the file at default_path, return a dict with uniform keys
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
        # the next line is a unique crypt implementation ID
        ret_val['crypt_id'] = cf.readline().strip('\n')
        # the next line is an encrypted datetime stamp
        ret_val['timestamp'] = cf.readline().strip('\n')
        # the next line is the encrypted content
        ret_val['body'] = cf.readline().strip('\n')
    return ret_val


def write(
        pth: Path,
        salt: str,
        crypt_id: str,
        timestamp: str,
        body: str,
        overwrite: bool = False,
        allow_empty: bool = False
) -> None:
    """
    Write the salt, timestamp, and body to the specified default_path file
    :param pth: Path object to write
    :param salt: salt value
    :param crypt_id: ID of crypt handler
    :param timestamp: timestamp
    :param body: body
    :param overwrite: whether to overwrite an existing file
    :param allow_empty: whether to allow writing file with no/empty body
    :return: None
    """
    if pth.exists() and not overwrite:
        raise FileExistsError(
            f"file {pth} already exists, and overwrite is False"
        )
    if not body and not allow_empty:
        raise AttributeError("Record has no content!")
    if (
            ("\n" in salt or "\n" in timestamp) or (body and "\n" in body)
    ):
        raise ValueError(
            f"File fields can not contain newline char\n"
            f"salt: [{salt}]\n"
            f"crypt_id: [{crypt_id}]\n"
            f"timestamp: [{timestamp}]\n"
            f"body: [{body}]\n"
        )
    with pth.open("w") as cipher_file:
        cipher_file.write(
            f"{salt}\n{crypt_id}\n{timestamp}\n{body}\n"
        )
    return


class PhibesRecordHandler(object):
    def __init__(self, *args):
        self.args = args

    def write(
            self, salt: str, crypt_id: str, timestamp: str, body: str
    ) -> str:
        """
        Return a multi-line str suitable for writing to file
        :param salt: salt value
        :param crypt_id: ID of crypt handler
        :param timestamp: timestamp
        :param body: body
        :return: str
        """
        if not body:
            raise AttributeError("Record has no content!")
        if (
                "\n" in salt
                or "\n" in crypt_id
                or "\n" in timestamp
        ) or (body and "\n" in body):
            raise ValueError(
                f"File fields can not contain newline char\n"
                f"salt: {salt}\n"
                f"crypt_id: {crypt_id}\n"
                f"timestamp: {timestamp}\n"
                f"body: {body}\n"
            )
        return f"{salt}\n{crypt_id}\n{timestamp}\n{body}\n"

    def __repr__(self):
        return
