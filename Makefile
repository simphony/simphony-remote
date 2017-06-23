SHELL=bash

.PHONY: venv
venv:
	@echo "Creating virtual environment"
	@echo "----------------------------"
	python3 -m venv venv

# Only use this on ubuntu-14.04 to retrieve a recent version of docker-engine. The docker.io default shipment with Trusty is
# too old for our software.
.PHONY: dockerengine
dockerengine:
	sudo apt-get -qq update
	sudo apt-get -qq install apt-transport-https ca-certificates software-properties-common
	sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
	sudo apt-get remove docker docker-engine
	sudo apt-get -qq update

.PHONY: deps
deps:
	@echo "Installing apt dependencies"
	@echo "---------------------------"
	if [ `uname -s` != "Linux" ]; then \
		echo "ERROR: Cannot run on non-Linux systems"; \
		false; \
	fi
	curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
	version_name=(shell lsb_release -cs)
	sudo add-apt-repository \
		"deb [arch=amd64] https://download.docker.com/linux/ubuntu \
		$(version_name) \
		stable"
	-sudo apt-get -qq update
	sudo apt-get install docker-ce=17.03.0~ce-0~ubuntu-$(lsb_release -cs)
	if [ `lsb_release -rs` = "14.04" ]; then \
		plat_packages="linux-image-extra-$(uname -r) linux-image-extra-virtual python3.4-venv"; \
	else \
		plat_packages="python3-venv"; \
	fi; \
		sudo apt-get -qq install -o Dpkg::Options::="--force-confold" --force-yes -y $$plat_packages nodejs python3-pip
	docker --version
	node --version
	npm --version
	npm install
	`npm bin`/bower install

.PHONY: pythondeps
pythondeps:
	pip3 -q install --upgrade pip setuptools
	pip3 -q install -r requirements.txt

.PHONY: devdeps
devdeps:
	@echo "Installing test dependencies"
	@echo "----------------------------"
	pip3 -q install -r dev-requirements.txt -r doc-requirements.txt
	sudo apt-get -qq install phantomjs

.PHONY: develop
develop:
	@echo "Installing application"
	@echo "----------------------"
	python3 setup.py -q develop

.PHONY: install
install:
	@echo "Installing application"
	@echo "----------------------"
	npm run build-test
	python3 setup.py -q install

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
        remoteappdb remoteappmanager.db init;\
        popd

.PHONY: testdb
testdb: db
	@echo "Creating Test database"
	@echo "----------------------"
	pushd jupyterhub; \
        remoteappdb remoteappmanager.db user create test; \
        remoteappdb remoteappmanager.db app create simphonyproject/simphonic-mayavi; \
        remoteappdb remoteappmanager.db app grant simphonyproject/simphonic-mayavi test; \
        popd

.PHONY: testimages
testimages:
	@echo "Downloading docker images"
	@echo "-------------------------"
	docker pull simphonyproject/simphonic-mayavi:latest
	if ! [ $$TRAVIS ]; then \
		docker pull simphonyproject/simphonic-paraview:latest \
		docker pull simphonyproject/filetransfer:latest; \
		docker pull simphonyproject/jupyter:latest; \
	fi


.PHONY: test
test: pythontest jstest

.PHONY: pythontest
pythontest:
	@echo "Running python testsuite"
	@echo "------------------------"
	python -m tornado.testing discover -s remoteappmanager -t .

.PHONY: jstest
jstest:
	@echo "Running javascript testsuite"
	@echo "----------------------------"
	`npm bin`/eslint --ext .vue,.js --ignore-path .eslintignore frontend/
	`npm bin`/node-qunit-phantomjs frontend/tests/tests.html

.PHONY: jscoverage
jscoverage:
	python -m http.server 12345 &
	open http://127.0.0.1:12345/jstests/tests.html?coverage

.PHONY: seleniumtest
seleniumtest:
	python -m unittest discover -s selenium_tests -t . -v

.PHONY: docs
docs:
	sphinx-build -W doc/source doc/build/sphinx
