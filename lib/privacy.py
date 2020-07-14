"""
Main library file for privacy_playground
"""
# core library modules
import base64
import hashlib

# third party packages
from Crypto.Cipher import AES
from Crypto import Random

# local project modules


BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


def encrypt(plain_text):
    return None


def decrypt(encrypted):
    return None
