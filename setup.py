"""
Package management script for setup tools.

For installation:
python setup.py install
To remove:
pip uninstall phibes

For development (will just create a link in site-packages):
python -m pip install -e .[develop]
except on zsh:
python -m pip install -e ".[develop]"
To remove:
pip uninstall phibes
"""

from setuptools import setup

setup()
