"""
Cryptography support
"""

# Built-in library packages
import hashlib
from typing import Optional

# Third party packages
from Cryptodome.Cipher import AES

# In-project modules
from phibes.crypto.crypt_ifc import CryptIfc


current_crypt_config = {
    "hash_algo": "sha256",
    "crypt_key_rounds": 100100,
    "auth_key_rounds": 100101,
    "key_bytes": 32,  # 256 bits
    "salt_bytes": 16,  # AES.block_size
    "name_bytes": 4,
    "mode": AES.MODE_CTR,
    "AES": {"mode": "MODE_CTR"}
}

available_versions = {
    "current": current_crypt_config
}


def get_crypt_version(version="current"):
    return available_versions.get(version)


def get_strong_hash(
        content: str,
        number_of_rounds: int,
        salt: str,
        length: int,
        hash_algo
) -> str:
    """
    Get a PDKDF2-based hash value for some string
    :param content: String to hash
    :param number_of_rounds: Number of rounds to iterate, integer
    :param salt: Hash salt, string containing valid hexadecimal
    :param length: Desired length of key in number of bytes
    :param hash_algo: Hash algorithm for hmac to use
    :return: hash value, in bytes
    """
    # Library dependency, so called function here *will* return bytes
    ret_val = hashlib.pbkdf2_hmac(
        hash_algo, content.encode(), bytes.fromhex(salt),
        number_of_rounds, dklen=length
    )
    return ret_val.hex()


def get_name_hash(name: str, version: Optional[str] = "current") -> str:
    """
    Return the one-way hash of the name.

    Uses the same hash method as used in encryption, but wouldn't have to.
    @param name: plaintext name string
    @type name: str
    @param version: affordance for future change of encryption/hash methods
    @type version: str
    @return: hashed result
    @rtype: str
    """
    ccv = get_crypt_version(version)
    return hashlib.pbkdf2_hmac(
        ccv.get("hash_algo"),
        name.encode(),
        bytes.fromhex('0000'),
        ccv.get("auth_key_rounds"),
        dklen=ccv.get("name_bytes")
    ).hex()


def new_get_name_hash(crypt_obj: CryptIfc, name: str):
    return crypt_obj.strong_hash(name, '0000', 4)
