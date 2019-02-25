# Makefile
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details

PKG_NAME := $(shell basename $(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
PKG_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
REPO_DIR ?= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SOURCE_DIR ?= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))/$(PKG_NAME)
EXTRA_DIR ?= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
### Custom pylint plugins configuration
PYLINT_PLUGINS_DIR := $(shell if [ -d $(EXTRA_DIR)/pylint_plugins ]; then echo "$(EXTRA_DIR)/pylint_plugins"; fi)
PYLINT_PLUGINS_LIST := $(shell if [ -d $(EXTRA_DIR)/pylint_plugins ]; then cd $(EXTRA_DIR)/pylint_plugins && ls -m *.py | sed 's|.*/||g' | sed 's|, |,|g' | sed 's|\.py||g'; fi)
PYLINT_CLI_APPEND := $(shell if [ -d $(EXTRA_DIR)/pylint_plugins ]; then echo "--load-plugins=$(PYLINT_PLUGINS_LIST)"; fi)
PYLINT_CMD := pylint \
	--rcfile=$(EXTRA_DIR)/.pylintrc \
	$(PYLINT_CLI_APPEND) \
	--output-format=colorized \
	--reports=no \
	--score=no
###

asort:
	@echo "Sorting Aspell whitelist"
	@$(PKG_DIR)/sbin/sort-whitelist.sh $(PKG_DIR)/data/whitelist.en.pws

bdist: meta
	@echo "Creating binary distribution"
	@cd $(PKG_DIR); python setup.py bdist

black:
	black \
		$(REPO_DIR) \
		$(SOURCE_DIR)/ \
		$(EXTRA_DIR)/tests \
		$(EXTRA_DIR)/docs \
		$(EXTRA_DIR)/docs/support

clean: FORCE
	@echo "Cleaning package"
	@rm -rf $(PKG_DIR)/.tox
	@find $(PKG_DIR) -name '*.pyc' -delete
	@find $(PKG_DIR) -name '__pycache__' -delete
	@find $(PKG_DIR) -name '.coverage*' -delete
	@find $(PKG_DIR) -name '*.tmp' -delete
	@find $(PKG_DIR) -name '*.pkl' -delete
	@find $(PKG_DIR) -name '*.error' -delete
	@rm -rf $(PKG_DIR)/build
	@rm -rf	$(PKG_DIR)/dist
	@rm -rf $(PKG_DIR)/docs/_build
	@rm -rf $(PKG_DIR)/$(PKG_NAME).egg-info
	@rm -rf $(PKG_DIR)/.cache
	@rm -rf $(PKG_DIR)/.eggs

distro: docs clean sdist wheel
	@rm -rf build $(PKG_NAME).egg-info

docs: FORCE
	@$(PKG_DIR)/sbin/build_docs.py $(ARGS)
	@cd $(PKG_DIR)/docs && make linkcheck

default:
	@echo "No default action"

FORCE:

lint:
	@echo "Running Pylint on package files"
	@PYTHONPATH="$(PYLINT_PLUGINS_DIR):$(PYTHONPATH)" $(PYLINT_CMD) $(REPO_DIR)/setup.py
	@PYTHONPATH="$(PYLINT_PLUGINS_DIR):$(PYTHONPATH)" $(PYLINT_CMD) $(SOURCE_DIR)
	@PYTHONPATH="$(PYLINT_PLUGINS_DIR):$(PYTHONPATH)" $(PYLINT_CMD) $(EXTRA_DIR)/sbin
	@PYTHONPATH="$(PYLINT_PLUGINS_DIR):$(PYTHONPATH)" $(PYLINT_CMD) $(EXTRA_DIR)/tests
	@PYTHONPATH="$(PYLINT_PLUGINS_DIR):$(PYTHONPATH)" $(PYLINT_CMD) $(EXTRA_DIR)/docs/support

meta: FORCE
	@echo "Updating package meta-data"
	@cd $(PKG_DIR)/sbin && ./update_copyright_notice.py
	@cd $(PKG_DIR)/sbin && ./update_sphinx_conf.py
	@cd $(PKG_DIR)/sbin && ./gen_req_files.py
	@cd $(PKG_DIR)/sbin && ./gen_pkg_manifest.py

sdist: meta
	@echo "Creating source distribution"
	@cd $(PKG_DIR) && python setup.py sdist --formats=gztar,zip
	@$(PKG_DIR)/sbin/list-authors.sh

sterile: clean
	@echo "Removing tox directory"
	@rm -rf $(PKG_DIR)/.tox

test: FORCE
	@$(PKG_DIR)/sbin/rtest.sh $(ARGS)

upload: lint distro
	@twine upload $(PKG_DIR)/dist/*

wheel: lint meta
	@echo "Creating wheel distribution"
	@$(PKG_DIR)/sbin/make_wheels.sh
	@$(PKG_DIR)/sbin/list-authors.sh
