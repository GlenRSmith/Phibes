"""
AES CTR-mode encryption
"""

# Built-in library packages
import base64

# Third party packages
from Cryptodome.Cipher import AES
from Cryptodome.Util import Counter

# In-project modules


def get_cipher(key: str, iv: str):
    """
    Get an AES counter-mode cipher object

    Which 'variety' of AES is determined by the key length.
    With AESn, n refers to the length of the key in bits.
    The supported lengths are 128, 192, and 256.
    :param key: encryption key
    :type key: str repr of hex value
    :param iv: counter initialization vector
    :type iv: str repr of hex value
    :return: cipher object
    :rtype: AES cipher, counter mode
    """
    key_bytes = bytes.fromhex(key)
    if len(key_bytes) not in [16, 24, 32]:
        raise ValueError(f"key {key} length {len(key)} not valid")
    iv_int = int.from_bytes(bytes.fromhex(iv), "big")
    return AES.new(
        key=key_bytes,
        mode=AES.MODE_CTR,
        counter=Counter.new(AES.block_size * 8, initial_value=iv_int)
    )


def encrypt(key: str, iv: str, plaintext: str) -> str:
    """

    :param key:
    :type key:
    :param iv:
    :type iv:
    :param plaintext:
    :type plaintext:
    :return:
    :rtype:
    """

    # convert from str to bytes
    plaintext_bytes = plaintext.encode('utf-8')
    # run the actual encryption - it gets bytes, returns bytes
    cipherbytes = get_cipher(key, iv).encrypt(plaintext_bytes)
    # substitute for chars that aren't file-system safe
    # e.g. - instead of + and _ instead of /
    # bytes in, bytes returned
    fs_safe_cipherbytes = base64.urlsafe_b64encode(cipherbytes)
    # convert the bytes to a utf-8 str
    return fs_safe_cipherbytes.decode('utf-8')


def decrypt(key: str, iv: str, ciphertext: str) -> str:
    # reverse the steps in `encrypt`
    # convert from str to bytes
    fs_safe_cipherbytes = ciphertext.encode('utf-8')
    # char substitution back to + and /
    cipherbytes = base64.urlsafe_b64decode(fs_safe_cipherbytes)
    # run the actual decryption
    plaintext_bytes = get_cipher(key, iv).decrypt(cipherbytes)
    # convert the bytes to utf-8 str
    return plaintext_bytes.decode('utf-8')
