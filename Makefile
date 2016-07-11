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

deps:
	@echo "Installing dependencies"
	@echo "-----------------------"
	sudo apt-get update
	sudo apt-get install docker-engine npm nodejs-legacy python3-pip python3.4-venv
	sudo npm install -g configurable-http-proxy

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

jupyterhub/test.crt:
	@echo "Creating certificates"
	@echo "---------------------"
	pushd scripts \
		&& sh generate_certificate.sh \
		&& cp test.* ../jupyterhub/ \
		&& popd

.PHONY: db
db: $(HOME)/remoteappmanager.db

$(HOME)/remoteappmanager.db:
	@echo "Creating database"
	@echo "-----------------"
	. venv/bin/activate && remoteappdb --db=~/remoteappmanager.db init

.PHONY: images
images:
	@echo "Downloading docker images"
	@echo "-------------------------"
	docker pull simphonyproject/ubuntu-14.04-remote:latest
	docker pull simphonyproject/simphonic-mayavi:latest
	docker pull simphonyproject/simphonic-paraview:latest
