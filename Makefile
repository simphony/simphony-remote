SHELL=bash

.PHONY: venv
venv:
	@echo "Creating virtual environment"
	@echo "----------------------------"
	python3 -m venv venv

.PHONY: deps
deps:
	@echo "Installing apt dependencies"
	@echo "---------------------------"
	if [ `uname -s` != "Linux" ]; then \
		echo "ERROR: Cannot run on non-Linux systems"; \
		false; \
	fi
	-sudo apt-get update
	if [ `lsb_release -rs` = "14.04" ]; then \
		plat_packages="docker-engine python3.4-venv"; \
	else \
		plat_packages="docker.io python3-venv"; \
	fi; \
		sudo apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y $$plat_packages npm nodejs-legacy python3-pip 

.PHONY: pythondeps
pythondeps:
	pip3 install --upgrade pip setuptools
	# Currently set to 1.4.0dev fixing X-Forward behavior
	npm install "git://github.com/jupyterhub/configurable-http-proxy.git#f54c6a46a235f17cb6c36046a913d37fa45ec95b"
	pip3 install -r requirements.txt 

.PHONY: devdeps
devdeps:
	@echo "Installing test dependencies"
	@echo "----------------------------"
	pip3 install -r dev-requirements.txt -r doc-requirements.txt
	sudo apt-get install phantomjs
	sudo npm install -g jshint
	sudo npm install -g node-qunit-phantomjs

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
        remoteappdb --db=remoteappmanager.db app create simphonyproject/simphonic-paraview; \
        remoteappdb --db=remoteappmanager.db app grant simphonyproject/simphonic-paraview test; \
        popd

.PHONY: testimages
testimages:
	@echo "Downloading docker images"
	@echo "-------------------------"
	docker pull simphonyproject/simphonic-mayavi:latest
	docker pull simphonyproject/simphonic-paraview:latest
	if ! [ $$TRAVIS ]; then \
		docker pull simphonyproject/filetransfer:latest; \
		docker pull simphonyproject/jupyter:latest; \
	fi
		

.PHONY: test
test: pythontest jstest

.PHONY: pythontest
pythontest:
	@echo "Running python testsuite"
	@echo "------------------------"
	flake8 . && python -m tornado.testing discover -s remoteappmanager -t . -v

.PHONY: jstest
jstest: 
	@echo "Running javascript testsuite"
	@echo "----------------------------"
	jshint --config .jshintrc remoteappmanager/static/js/
	node-qunit-phantomjs jstests/tests.html

.PHONY: docs
docs:
	sphinx-build -W doc/source doc/build/sphinx
