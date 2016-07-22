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

.PHONY: deps
deps:
	@echo "Installing dependencies"
	@echo "-----------------------"
	sudo apt-get update
	sudo apt-get install docker-engine npm nodejs-legacy python3-pip python3.4-venv
	sudo pip install --upgrade pip
	sudo npm install -g configurable-http-proxy
	python3 -mvenv venv
	. venv/bin/activate && \
		pip3 install docker-py && \
		pip3 install -r requirements.txt \
					-r dev-requirements.txt \
					-r doc-requirements.txt

.PHONY: develop
develop: 
	@echo "Installing application"
	@echo "----------------------"
	. venv/bin/activate && python3 setup.py develop 

.PHONY: install
install: 
	@echo "Installing application"
	@echo "----------------------"
	. venv/bin/activate && python3 setup.py install

.PHONY: certs
certs: 
	@echo "Creating certificates"
	@echo "---------------------"
	-pushd jupyterhub && sh ../scripts/generate_certificate.sh && popd

.PHONY: db
db: 
	@echo "Creating database"
	@echo "-----------------"
	-. venv/bin/activate && remoteappdb --db=~/remoteappmanager.db init

.PHONY: images
images:
	@echo "Downloading docker images"
	@echo "-------------------------"
	docker pull simphonyproject/ubuntu-14.04-remote:latest
	docker pull simphonyproject/simphonic-mayavi:latest
	docker pull simphonyproject/simphonic-paraview:latest

.PHONY: test
test:
	@echo "Running testsuite"
	@echo "-----------------"
	-. venv/bin/activate && flake8 . && python -m tornado.testing discover -s tests
