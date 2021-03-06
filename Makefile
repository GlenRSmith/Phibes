# Shell to use with Make
#SHELL := /bin/zsh

# Set important Paths
PROJECT := phibes
LOCALPATH := $(CURDIR)/$(PROJECT)
PYTHONPATH := $(LOCALPATH)/
PYTHON_BIN := $(VIRTUAL_ENV)/bin

.PHONY: list
list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

clean:
	echo "TODO"
	find . -name "*.pyc" -print0 | xargs -0 rm -rf
	-rm -rf .coverage
	-rm -rf build
	-rm -rf dist
	-rm -rf $(PROJECT).egg-info

build:
	pytest phibes
	python setup.py sdist
	python setup.py bdist_wheel --universal

which:
	which python

test:
	pytest --workers auto --verbose tests

cover:
	pytest --workers auto --cov-report term-missing --cov=phibes tests -m negative
	pytest --workers auto --cov-report term-missing --cov=phibes tests -m positive

flake:
	flake8 src/phibes

test_all_p:
	flake8 phibes
	pytest --workers auto --cov=phibes -m positive --cov-fail-under=75
	pytest --workers auto --cov=phibes -m negative --cov-fail-under=65
	pytest -m 'not positive and not negative'

test_all:
	flake8 src/phibes
	pytest --cov=phibes -m positive --cov-fail-under=75
	pytest --cov=phibes -m negative --cov-fail-under=65
	pytest -m 'not positive and not negative'

find_unmarked_tests:
	pytest --co -m "not negative and not positive"

publish_pypi:
	python3 -m twine upload --repository pypi dist/*

publish_test_pypi:
	python3 -m twine upload --repository testpypi dist/*
