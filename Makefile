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

.PHONY: aptdeps
aptdeps:
	@echo "Installing apt dependencies"
	@echo "---------------------------"
	sudo apt-get update
	sudo apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y docker-engine npm nodejs-legacy python3-pip python3.4-venv
	sudo pip install --upgrade pip
	sudo npm install -g configurable-http-proxy

.PHONY: pythondeps
pythondeps:
	@echo "Installing dependencies"
	@echo "-----------------------"
	if test -z "${NO_VENV}"; \
	then \
		echo "Installing virtual env."; \
		python3 -m venv venv; \
		. venv/bin/activate; \
	fi; \
	pip3 install -r requirements.txt -r dev-requirements.txt -r doc-requirements.txt

.PHONY: deps
deps: aptdeps pythondeps

.PHONY: develop
develop: 
	@echo "Installing application"
	@echo "----------------------"
	if test -z ${NO_VENV}; \
	then \
		. venv/bin/activate; \
	fi; \
	python3 setup.py develop

.PHONY: install
install: 
	@echo "Installing application"
	@echo "----------------------"
	if test -z ${NO_VENV}; \
	then \
		. venv/bin/activate; \
	fi; \
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
	if test -z ${NO_VENV}; \
	then \
		. venv/bin/activate; \
	fi; \
	pushd jupyterhub; \
        remoteappdb --db=remoteappmanager.db init;\
        remoteappdb --db=remoteappmanager.db user create test; \
        remoteappdb --db=remoteappmanager.db app create simphonyproject/simphonic-mayavi; \
        remoteappdb --db=remoteappmanager.db app grant simphonyproject/simphonic-mayavi test; \
        popd

.PHONY: images
images:
	@echo "Downloading docker images"
	@echo "-------------------------"
	docker pull simphonyproject/simphonic-mayavi:latest

.PHONY: test
test:
	@echo "Running testsuite"
	@echo "-----------------"
	if test -z ${NO_VENV}; \
	then \
		. venv/bin/activate; \
	fi; \
	flake8 . && python -m tornado.testing discover -s tests -t . -v

.PHONY: docs
docs:
	if test -z ${NO_VENV}; \
	then \
		. venv/bin/activate; \
	fi; \
	sphinx-build -W doc/source doc/build/sphinx
