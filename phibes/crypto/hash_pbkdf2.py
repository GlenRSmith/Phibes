"""
Module to support PBKDF2-based hashing
"""


# Built-in library packages
import enum
import hashlib

# Third party packages


class HashAlg(enum.Enum):
    SHA256 = 'SHA256'
    SHA512 = 'SHA512'


def pbkdf2(
        hash_alg: HashAlg,
        seed: str,
        salt: str,
        rounds: int,
        key_length: int = None
) -> str:
    """

    @param hash_alg: Hashing algorithm to iterate as pseudo-random function
    @type hash_alg: HashAlg
    @param seed: The plaintext value to be hashed (e.g. a password)
    @type seed: str
    @param salt: Crypto salt, pbkdf2_hmac accepts any length,
    16+ bytes is suggested, 16 bytes matches AES.block_size
    @type salt: str
    @param rounds:
    @type rounds:
    @param key_length: `dklen` is requested length of key (in bytes)
    If dklen is None, the digest size of the hash algorithm is used
    SHA512 returns 128 characters: 64 bytes.
    SHA256 returns 64 characters: 32 bytes.
    @type key_length: int
    @return: the result of the hashing operation in hexadecimal string form
    @rtype: str
    """
    seed_bytes = seed.encode('utf-8')
    salt_bytes = bytes.fromhex(salt)
    return hashlib.pbkdf2_hmac(
        hash_alg.value, seed_bytes, salt_bytes, rounds, dklen=key_length
    ).hex()


def pbkdf2_sha256(seed, salt, rounds, key_length=None):
    return pbkdf2(HashAlg.SHA256, seed, salt, rounds, key_length)


def pbkdf2_sha512(seed, salt, rounds, key_length=None):
    return pbkdf2(HashAlg.SHA512, seed, salt, rounds, key_length)
