# Built-in library packages

# local project
from phibes.crypto.factory import create_crypt, get_crypt, list_crypts
from phibes.crypto.factory import register_crypt, register_default_crypt
from phibes.crypto.crypt_aes_ctr_sha import Aes128CtrPbkdf2Sha256
# from phibes.crypto.crypt_aes_ctr_sha import Aes128CtrPbkdf2Sha512
# from phibes.crypto.crypt_aes_ctr_sha import Aes192CtrPbkdf2Sha256
# from phibes.crypto.crypt_aes_ctr_sha import Aes192CtrPbkdf2Sha512
from phibes.crypto.crypt_aes_ctr_sha import Aes256CtrPbkdf2Sha256
from phibes.crypto.crypt_aes_ctr_sha import Aes256CtrPbkdf2Sha512
from phibes.crypto.crypt_plain_plain import CryptPlainPlain

register_crypt(CryptPlainPlain)
aes128_256 = register_crypt(
    Aes128CtrPbkdf2Sha256, key_rounds=100100
)
# aes128_512 = register_crypt(
#     Aes128CtrPbkdf2Sha512, key_rounds=100100, fallback_id=aes128_256,
# )
# aes192_256 = register_crypt(
#     Aes192CtrPbkdf2Sha256, key_rounds=100100, fallback_id=aes128_256
# )
# aes192_512 = register_crypt(
#     Aes192CtrPbkdf2Sha512, key_rounds=100100, fallback_id=aes192_256,
# )
aes256_256 = register_crypt(
    Aes256CtrPbkdf2Sha256, key_rounds=100100, fallback_id=aes128_256
)
aes256_512 = register_default_crypt(
    Aes256CtrPbkdf2Sha512, key_rounds=100100, fallback_id=aes256_256,
)
default_id = aes256_512


__all__ = [
    "create_crypt", "get_crypt", "list_crypts", "register_crypt",
    "register_default_crypt", "default_id"
]
