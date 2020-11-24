"""
Module to support PBKDF2-based hashing
"""

# Built-in library packages
import enum
import hashlib

# Third party packages

# In project


class HashAlg(enum.Enum):
    SHA256 = 'SHA256'
    SHA512 = 'SHA512'


def pbkdf2(
        hash_alg: str,
        seed: str,
        salt: str,
        rounds: int,
        key_length: int = None
) -> str:
    """

    @param hash_alg: Hashing algorithm to iterate as pseudo-random function
    @param seed: The plaintext value to be hashed (e.g. a password)
    @param salt: Crypto salt, pbkdf2_hmac accepts any length,
    16+ bytes is suggested, 16 bytes matches AES.block_size
    @param rounds: number of hashing iterations
    @param key_length: `dklen` is requested length of key (in bytes)
    If dklen is None, the digest size of the hash algorithm is used
    SHA512 returns 128 characters: 64 bytes.
    SHA256 returns 64 characters: 32 bytes.
    @return: the result of the hashing operation in hexadecimal string form
    """
    hash_alg = HashAlg(hash_alg.upper().replace('-', ''))
    seed_bytes = seed.encode('utf-8')
    salt_bytes = bytes.fromhex(salt)
    ret_val = hashlib.pbkdf2_hmac(
        hash_alg.value, seed_bytes, salt_bytes, rounds, dklen=key_length
    ).hex()
    return ret_val
