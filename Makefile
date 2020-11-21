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
#	find . -name "*.pyc" -print0 | xargs -0 rm -rf
#	-rm -rf .coverage
#	-rm -rf build
#	-rm -rf dist
#	-rm -rf $(PROJECT).egg-info

build:
	pytest phibes

which:
	which python

test:
	pytest --verbose tests

cover:
	pytest --cov-report term-missing --cov=phibes tests -m negative
	pytest --cov-report term-missing --cov=phibes tests -m positive

flake:
	flake8 phibes

test_all:
	pytest --cov=phibes -m positive --cov-fail-under=75
	pytest --cov=phibes -m negative --cov-fail-under=65
	pytest -m 'not positive and not negative'
	flake8 phibes

find_unmarked_tests:
	pytest --co -m "not negative and not positive"
