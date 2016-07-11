OS=$(shell uname)

.PHONY: help
help:
	@echo "Please specify one of the following:"
	@echo ""
	@echo "deps: install the dependencies of the project for your platform"
	@echo "install: install the application"
	@echo "check: performs sanity checks for the installation"

.PHONY: deps
deps:
	echo "deps"

.PHONY: install
install:
	echo "install"

.PHONY: check
check:
	echo "check"
