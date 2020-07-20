"""
Implementation of Secrets

A Secret is an entry in a Locker.
"""

# Built-in library packages
import secrets

# Third party packages

# In-project modules

KEY_BYTES = 32
SALT_BYTES = 16


class Secret(object):

    @classmethod
    def find(cls, name, locker):
        secret_name = locker.encrypt(name)
        secret_file = locker.locker_path.joinpath(
            f"{secret_name}.sct"
        )
        if secret_file.exists():
            with open(f"{secret_file}", "r") as s_file:
                # the salt was stored in hexadecimal form, with a line feed
                salt = s_file.readline().strip('\n')
                # the next line in the file is the encrypted secret
                ciphertext = s_file.readline().strip('\n')
                plaintext = locker.decrypt(ciphertext, salt=salt).decode()
            return plaintext
        else:
            return None

    def __init__(self, name, locker, create=False, secret_text=None):
        self.name = name
        self.locker = locker
        self.salt = None
        # self.ciphertext = None
        self.secret_name = None
        # don't want to even expose the plaintext name
        self.secret_name = self.locker.encrypt(self.name)
        self.secret_file = locker.locker_path.joinpath(
            f"{self.secret_name}.sct"
        )
        if create:
            if self.secret_file.exists():
                raise ValueError(f"Secret {name} already exists")
            if secret_text is None:
                raise ValueError(f"The secret {name} requires some content!")
            else:
                # safely get random bytes, turn into string hexadecimal
                self.salt = secrets.token_bytes(SALT_BYTES).hex()
                ciphertext = self.locker.encrypt(
                    secret_text, salt=self.salt
                )
                with open(self.secret_file, "w") as cipher_file:
                    cipher_file.write(f"{self.salt}\n{ciphertext}\n")
        else:
            if secret_text is not None:
                msg = f"Secret.__init__ can't take text without create=True"
                details = f"{name} {secret_text}"
                raise ValueError(msg + details)
            with open(f"{self.secret_file}", "r") as s_file:
                # the salt was stored in hexadecimal form, with a line feed
                self.salt = s_file.readline().strip('\n')
                # the next line in the file is the encrypted secret
                ciphertext = s_file.readline().strip('\n')
                self.plaintext = self.locker.decrypt(
                    ciphertext, salt=self.salt
                ).decode()
        super().__init__()  # is this best practice?

    def update(self, secret_text):
        """
        Method to overwrite an existing secret
        :param secret_text: new secret text to encrypt
        :return:
        """
        # safely get random bytes, turn into string hexadecimal
        self.salt = secrets.token_bytes(SALT_BYTES).hex()
        ciphertext = self.locker.encrypt(secret_text, salt=self.salt)
        with open(self.secret_file, "w") as cipher_file:
            cipher_file.write(f"{self.salt}\n{ciphertext}\n")
        return
