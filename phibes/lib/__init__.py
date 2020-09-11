# Built-in library packages
# from typing import Optional

# Third party packages

# from phibes.crypto import crypt_factory


# class AesCtrPbkdf2Sha256SvcBld(object):
#
#     impl_id = "aes256pbkdf2sha256"
#
#     def __init__(self):
#         # Don't mistake this for a singleton pattern
#         # This is just lazy instantiation, not creating _instance
#         # when *this* class is instanced for registration
#         self._instance = None
#
#     def __call__(self, password, salt=None, **_ignored):
#         if not self._instance:
#             self._instance = CryptAes256CtrPbkdf2Sha256(
#                 password,
#                 crypt_key_rounds=100100,
#                 salt=salt
#             )
#             self._instance.impl_id = self.impl_id
#         return self._instance
#
#
# CryptFactory().register_builder(
#     "AesCtrPbkdf2Sha256SvcBld",
#     AesCtrPbkdf2Sha256SvcBld()
# )
