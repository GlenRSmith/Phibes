#!/usr/bin/env python
"""
Command-line interface to python privacy playground admin
"""

# core library modules
from __future__ import annotations
import json

# third party packages
import click

# In-project modules
from lib import config


@click.group()
def main():
    pass


@main.command()
def configure():
    print(f"configure me!")


def encrypt_save(func):
    def dec(self):
        old_member = self.myMember
        func(self)
        self.myMember = old_member
        return
    return dec


class Toto(object):

    @property
    def content(self):
        # want to interact with `content` as a set,
        # but to have _secrets be a string
        return self._secrets

    @content.setter
    def content(self, new_content):
        self._secrets = new_content
        return

    def __init__(self):
        self.my_member = []
        self._secrets = None

    def update(self, var):
        self.my_member.append(var)

    @encrypt_save
    def do_job(self):
        self.update('haha!!')
        print(f"doJob: {self.my_member.__repr__()}")


class B(Toto):

    def __init__(self):
        super().__init__()
        self.content = set()

    @property
    def content(self):
        if not super(B, self).content:
            bar = set()
        else:
            bar = set(json.loads(super(B, self).content))
        print(f"getter bar {bar}")
        return bar

    @content.setter
    def content(self, value):
        print(f"setter value {value}")
        print(f"setter dump {json.dumps(list(value))}")
        super(B, self.__class__).content.__set__(
            self, json.dumps(list(value))
        )

    def add_secret(self, secret):
        print(f"add_secret {secret}")
        stage1 = self.content
        stage1.add(secret)
        self.content = stage1
        # self.content.add(secret)
        print(f"add_secret self._{self._secrets}")

    def list_secrets(self):
        print(f"secrets: {self._secrets}")


@main.command()
@click.option('--name', prompt='name', default="my_name")
def go(name):
    print(f"go({name})")
    foo = B()
    foo.add_secret("first")
    foo.add_secret("second")
    foo.add_secret("third")
    foo.list_secrets()


# @main.command()
# def read_conf():
#     my_conf = config.Config()
#     click.echo(my_conf)


# @main.command()
# @click.option(
#     '--path',
#     prompt='installation path',
#     default=config.get_system_path().absolute()
# )
# @click.option(
#     '--proceed',
#     prompt='only default path supported, proceed?',
#     default=False
# )
# def init(path, proceed):
#     if proceed:
#         config.system_install(path)


if __name__ == '__main__':
    main()
