SHELL=bash

.PHONY: help
help:
	@echo "Please specify one of the following:"
	@echo ""
	@echo "deps: install the dependencies of the project for your platform"
	@echo "install: install the application"
	@echo "certs: builds and installs the certificates"
	@echo "images: installs basic simphony images"
	@echo "db: initializes the sqlite database"
	@echo ""

.PHONY: venv
venv:
	@echo "Creating virtual environment"
	@echo "----------------------------"
	python3 -m venv venv

.PHONY: aptdeps
aptdeps:
	@echo "Installing apt dependencies"
	@echo "---------------------------"
	sudo add-apt-repository ppa:mc3man/trusty-media
	-apt-get update
	apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y docker-engine npm nodejs-legacy python3-pip python3.4-venv ffmpeg
	pip install --upgrade pip
	npm install -g configurable-http-proxy

.PHONY: pythondeps
pythondeps:
	@echo "Installing dependencies"
	@echo "-----------------------"
	pip3 install -r requirements.txt -r dev-requirements.txt -r doc-requirements.txt

.PHONY: develop
develop: 
	@echo "Installing application"
	@echo "----------------------"
	python3 setup.py develop

.PHONY: install
install:
	@echo "Installing application"
	@echo "----------------------"
	python3 setup.py install

.PHONY: certs
certs: 
	@echo "Creating certificates"
	@echo "---------------------"
	-pushd jupyterhub && sh ../scripts/generate_certificate.sh && popd

.PHONY: db
db: 
	@echo "Creating database"
	@echo "-----------------"
	pushd jupyterhub; \
        remoteappdb --db=remoteappmanager.db init;\
        popd

.PHONY: testdb
testdb: db
	@echo "Creating Test database"
	@echo "----------------------"
	pushd jupyterhub; \
        remoteappdb --db=remoteappmanager.db user create test; \
        remoteappdb --db=remoteappmanager.db app create simphonyproject/simphonic-mayavi; \
        remoteappdb --db=remoteappmanager.db app grant simphonyproject/simphonic-mayavi test; \
        popd

.PHONY: testimages
testimages:
	@echo "Downloading docker images"
	@echo "-------------------------"
	docker pull simphonyproject/simphonic-mayavi:latest

.PHONY: test
test:
	@echo "Running testsuite"
	@echo "-----------------"
	flake8 . && python -m tornado.testing discover -s tests -t . -v

.PHONY: docs
docs:
	sphinx-build -W doc/source doc/build/sphinx
