"""
Cryptography support
"""

# Built-in library packages
import base64

# Third party packages

# In-project modules
from . crypto import get_cipher, make_crypt_key, make_salt_string


class CryptImpl(object):

    def __init__(
            self,
            crypt_arg,
            crypt_arg_is_key: bool = True,
            iv: str = make_salt_string()
    ):
        if crypt_arg_is_key:
            self.key = crypt_arg
        else:
            self.key = make_crypt_key(crypt_arg, iv)
        self.iv, self.cipher = get_cipher(
            self.key, iv=bytes.fromhex(iv)
        )
        return

    def _refresh_cipher(self):
        self.iv, self.cipher = get_cipher(self.key, self.iv)

    def encrypt(self, plaintext: str) -> str:
        cipherbytes = self.cipher.encrypt(plaintext.encode('utf-8'))
        ret_val = base64.urlsafe_b64encode(cipherbytes).decode('utf-8')
        self._refresh_cipher()
        return ret_val

    def decrypt(self, ciphertext: str):
        cipherbytes = base64.urlsafe_b64decode(ciphertext)
        ret_val = self.cipher.decrypt(cipherbytes)
        self._refresh_cipher()
        return ret_val

    def __str__(self):
        return (
            f"key: {self.key} - type: {type(self.key)}\n"
            f"iv: {self.iv} - type: {type(self.iv)}\n"
            f"key: {self.key.hex()} - type: {type(self.key.hex())}\n"
            f"iv: {self.iv.hex()} - type: {type(self.iv.hex())}\n"
        )
