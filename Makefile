SHELL=bash
OS=$(shell uname)

.PHONY: help
help:
	@echo "Please specify one of the following:"
	@echo ""
	@echo "all: full deployment"
	@echo "deps: install the dependencies of the project for your platform"
	@echo "install: install the application"
	@echo "certs: builds and installs the certificates"
	@echo "db: initializes the sqlite database"
	@echo "check: performs sanity checks for the installation"
	@echo ""

.PHONY: deps
ifeq ($(OS), Darwin)
deps:
	echo "deps"
else # Linux
deps:
	@echo "Installing dependencies"
	@echo "-----------------------"
	sudo apt-get install npm nodejs-legacy python3-pip python3.4-venv
	sudo npm install -g configurable-http-proxy
endif

.PHONY: install
install: 
	@echo "Installing application"
	@echo "----------------------"
	python3 -mvenv venv
	. venv/bin/activate \
		&& pip3 install docker-py \
		&& python3 setup.py develop 

.PHONY: certs
certs: jupyterhub/test.crt
	@echo "Creating certificates"
	@echo "---------------------"
	pushd scripts \
		&& sh generate_certificate.sh \
		&& cp test.* ../jupyterhub/ \
		&& popd

.PHONY: db
db: 
	@echo "Creating database"
	@echo "-----------------"
	. venv/bin/activate && remoteappdb --db=~/remoteappmanager.db init

.PHONY: check
check:
	echo "check"
