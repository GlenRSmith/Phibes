"""
Cryptography support
"""

# Built-in library packages
import base64
import hashlib
import secrets
from typing import Optional

# Third party packages
from Cryptodome.Cipher import AES
from Cryptodome.Util import Counter

# In-project modules

current_crypt_config = {
    "hash_algo": "sha256",
    "crypt_key_rounds": 100100,
    "auth_key_rounds": 100101,
    "key_bytes": 32,  # 256 bits
    "salt_bytes": 16,  # AES.block_size
    "name_bytes": 4,
    "mode": AES.MODE_CTR
}

available_versions = {
    "current": current_crypt_config
}


def determine_valid_version(salt, key, password, ciphertext):
    for ver in available_versions:
        try:
            impl = CryptImpl(
                crypt_arg=key,
                crypt_arg_is_key=True,
                salt=salt,
                version=ver
            )
            if impl.authenticate(password, ciphertext):
                return ver
            else:
                continue
        except Exception as err:
            print(err)
            continue
    raise ValueError("no matching encryption found")


def get_crypt_version(version="current"):
    return available_versions.get(version)


def encrypt(key: str, plaintext: str, iv: Optional[str] = None) -> str:
    """
    Encrypt some plaintext
    :param key: 32-byte encryption key
    :param plaintext: text to be encrypted, arbitrary length
    :param iv: initialization vector, optional, 16-bytes
    :return: iv, ciphertext
    """
    return CryptImpl(key, crypt_arg_is_key=True, salt=iv).encrypt(plaintext)


def decrypt(key: str, ciphertext: str, iv: str):
    """
    Decrypt a ciphertext
    :param key: 32-byte encryption key
    :param ciphertext: the encrypted text to decrypt
    :param iv: initialization vector, 16-bytes
    :return: plaintext from decryption
    """
    return CryptImpl(key, crypt_arg_is_key=True, salt=iv).decrypt(ciphertext)


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
    :return: hash value, in bytes
    """
    # Library dependancy, so called function here *will* return bytes
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


class CryptImpl(object):

    @property
    def salt(self):
        """
        salt property accessor
        :return:
        """
        return self._salt

    @salt.setter
    def salt(self, new_salt: str):
        """
        salt property mutator
        :param new_salt:
        :return:
        """
        self._salt = new_salt
        self._refresh_cipher(new_salt)
        return

    def __init__(
            self,
            crypt_arg: str,
            crypt_arg_is_key: Optional[bool] = True,
            salt: Optional[str] = None,
            version: Optional[str] = "current"
    ):
        ccv = get_crypt_version(version)
        self.salt_len = ccv.get("salt_bytes")
        self.rounds = ccv.get("crypt_key_rounds")
        self.key_bytes = ccv.get("key_bytes")
        self.hash_algo = ccv.get("hash_algo")
        if salt:
            # `len` is character length, twice byte length
            if len(salt) != self.salt_len * 2:
                raise ValueError(
                    f"salt must be {self.salt_len} bytes long\n"
                    f"{salt} is {len(salt)/2} bytes long"
                )
        else:
            salt = secrets.token_hex(self.salt_len)
        self._salt = salt
        if crypt_arg_is_key:
            # client already has encryption key
            self.key = crypt_arg
        else:
            # creating a new encryption key
            try:
                self.key = get_strong_hash(
                    crypt_arg,
                    self.rounds,
                    salt,
                    self.key_bytes,
                    self.hash_algo
                )
            except TypeError as err:
                raise err
        self._refresh_cipher(salt)
        return

    def encrypt(self, plaintext: str) -> str:
        # convert from str to bytes
        plaintext_bytes = plaintext.encode('utf-8')
        # run the actual encryption - it gets bytes, returns bytes
        cipherbytes = self.cipher.encrypt(plaintext_bytes)
        # substitute for chars that aren't file-system safe
        # e.g. - instead of + and _ instead of /
        # it gets bytes, returns bytes
        fs_safe_cipherbytes = base64.urlsafe_b64encode(cipherbytes)
        # convert the bytes to a utf-8 str
        ret_val = fs_safe_cipherbytes.decode('utf-8')
        self._refresh_cipher(self._salt)
        return ret_val

    def decrypt(self, ciphertext: str) -> str:
        # reverse the steps in `encrypt`
        # convert from str to bytes
        fs_safe_cipherbytes = ciphertext.encode('utf-8')
        # char substitution back to + and /
        cipherbytes = base64.urlsafe_b64decode(fs_safe_cipherbytes)
        # run the actual decryption
        plaintext_bytes = self.cipher.decrypt(cipherbytes)
        # convert the bytes to utf-8 str
        ret_val = plaintext_bytes.decode('utf-8')
        self._refresh_cipher(self.salt)
        return ret_val

    def encrypt_password(self, password: str) -> str:
        """
        Performs a hash on the password, then encrypts the hash
        @param password: password to encrypt
        @type password: str
        @return: encrypted value
        @rtype: str
        """
        return encrypt(
            self.key,
            get_strong_hash(
                password,
                self.rounds,
                self.salt,
                length=self.key_bytes,
                hash_algo=self.hash_algo
            ),
            self.salt
        )

    def authenticate(self, password: str, cipher: str):
        """
        Run the submitted password through the same hash+encryption
        that produced the cipher, and compare
        :param password: Submitted password
        :param cipher: The canonical hash, encrypted value
        :return:
        """
        return cipher == self.encrypt_password(password)

    def _refresh_cipher(self, salt: str):
        """
        Create a new cipher instance - least complicated way to
        avoid exceptions like "can't encrypt after decrypt" and vice-versa
        :param salt:
        :return:
        """
        key_bytes = bytes.fromhex(self.key)
        if not len(key_bytes) == self.key_bytes:
            raise ValueError(
                f"`key` arg must be exactly {self.key_bytes} long\n"
                f"{key_bytes} (from key:{self.key}) is {len(key_bytes)}"
            )
        self.cipher = AES.new(
            key=key_bytes,
            mode=AES.MODE_CTR,
            counter=Counter.new(
                AES.block_size * 8,
                initial_value=int.from_bytes(bytes.fromhex(salt), "big")
            )
        )
        return

    def __str__(self):
        return (
            f"key: {self.key} - type: {type(self.key)}\n"
            f"iv: {self.salt} - type: {type(self.salt)}"
        )
