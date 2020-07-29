"""
Implementation of Schema

A Schema is used to enforce format on other entities, like Tags.
"""

# Built-in library packages
import json

# Third party packages

# In-project modules


class Schema(object):

    def __init__(self):
        self.secrets = set()
        return

    def add_secret(self, secret):
        self.secrets.add(secret)
        return

    def remove_secret(self, secret):
        self.secrets.remove(secret)
        return

    def list_secrets(self):
        return list(self.secrets)

    def read_from_file(self, file_path):
        with open(file_path, 'r') as tagfile:
            data = json.load(tagfile)
            self.secrets = data["secrets"]
        return

    def write_to_file(self, file_path):
        with open(file_path, 'w') as tagfile:
            tagfile.write(str(self))
        return

    def __str__(self):
        data = dict()
        data['secrets'] = list(self.secrets)
        return json.dumps(data, indent=4)
