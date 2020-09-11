# Built-in library packages

# local project
# from phibes.crypto.crypt_ifc import CryptIfc
# from phibes.crypto.factory import CryptFactory
from phibes.crypto.factory import create_crypt, get_crypt, list_crypts
from phibes.crypto.factory import register_crypt
from phibes.crypto.crypt_aes256ctr_sha256 import CryptAesCtrPbkdf2Sha256


register_crypt(CryptAesCtrPbkdf2Sha256, {'key_rounds': 100100})


__all__ = [
    "create_crypt", "get_crypt", "list_crypts", "register_crypt"
]
