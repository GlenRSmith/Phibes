# Built-in library packages

# local project
from phibes.crypto.factory import create_crypt, get_crypt, list_crypts
from phibes.crypto.factory import register_crypt, register_default_crypt
from phibes.crypto.crypt_aes_ctr_sha256 import CryptAesCtrPbkdf2Sha
from phibes.crypto.crypt_plain_plain import CryptPlainPlain

register_crypt(CryptPlainPlain, length_bytes=8)
first_id = register_crypt(
    CryptAesCtrPbkdf2Sha, key_rounds=100100, hash_alg='SHA256'
)
default_id = register_default_crypt(
    CryptAesCtrPbkdf2Sha, fallback_id=first_id, key_rounds=100100,
    hash_alg='SHA512'
)


__all__ = [
    "create_crypt", "get_crypt", "list_crypts", "register_crypt",
    "register_default_crypt", "default_id"
]
