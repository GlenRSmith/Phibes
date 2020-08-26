"""
Package management script for setup tools.

For installation:
python setup.py install
To remove:
pip uninstall phibes

For development (will just create a link in site-packages):
python setup.py develop
To remove:
python setup.py develop -u
"""

from setuptools import setup

setup(name="phibes", packages=["."])
