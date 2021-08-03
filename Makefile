SHELL=bash
NODEJS_VERSION=6
SIMPHONY_REMOTE=`pwd`
CERT_TYPE='test'

OS_DEPS = curl ca-certificates nginx

UBUNTU_PKG = apt-get
CENTOS_PKG = yum

UBUNTU_DEPS = gnupg-agent apt-transport-https software-properties-common
CENTOS_DEPS = openssl device-mapper-persistent-data lvm2 bzip2 gcc-c++ epel-release

PYTHON3_DEPS = python3 python3-pip python3-venv
DOCKER_DEPS = docker-ce docker-ce-cli containerd.io


.PHONY: venv
venv:
	@echo "Creating virtual environment"
	@echo "----------------------------"
	python3 -m venv venv

.PHONY: deps
deps:
	@echo "Installing dependencies"
	@echo "---------------------------"
	if [ `uname -s` != "Linux" ]; then \
		echo "ERROR: Cannot run on non-Linux systems"; \
		false; \
	fi

	if [ -f "/etc/lsb-release" ]; then \
		$(MAKE) ubuntudeps; \
	elif [ -f "/etc/centos-release" ]; then \
		$(MAKE) centosdeps; \
	else \
		echo "ERROR: Installation requires either Ubuntu or CentOS systems"; \
		false; \
	fi

osdeps:

	# Install OS Dependencies
	sudo $(PKG_MNGR) update -y
	sudo $(PKG_MNGR) install -y $(OS_DEPS)

	# Download and install NodeJS
	curl -sL https://$(OS).nodesource.com/setup_${NODEJS_VERSION}.x | sudo -E bash -
	sudo $(PKG_MNGR) install -y nodejs

	# Install NPM if missing
	$(MAKE) npmdeps PKG_MNGR=$(PKG_MNGR)

ubuntudeps:

	# Install Ubuntu Dependencies
	sudo $(UBUNTU_PKG) install -qq -y $(UBUNTU_DEPS)

	# Install generic OS dependencies
	$(MAKE) osdeps PKG_MNGR=$(UBUNTU_PKG) OS=deb

	# Download and install Docker
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
	sudo apt-key adv --keyserver hkps://sks.pod02.fleetstreetops.com --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
	sudo add-apt-repository \
		"deb [arch=amd64] https://download.docker.com/linux/ubuntu \
		`lsb_release -cs` \
		stable"
	$(MAKE) dockerdeps PKG_MNGR=$(UBUNTU_PKG)

	# Install Python 3
	if [ `lsb_release -cs` == "xenial" ] || [ `lsb_release -cs` == "trusty" ]; then \
		 sudo $(UBUNTU_PKG) install -o Dpkg::Options::="--force-confold" --force-yes -y linux-image-extra-virtual linux-image-extra-`uname -r` $(PYTHON3_DEPS); \
	else sudo $(UBUNTU_PKG) install -o Dpkg::Options::="--force-confold" --force-yes -y $(PYTHON3_DEPS); \
	fi

	# Update if needed
	sudo $(UBUNTU_PKG) update -y

centosdeps:

	# Install CentOS Dependencies
	sudo $(CENTOS_PKG) install -y $(CENTOS_DEPS)

	# Install generic OS dependencies
	$(MAKE) osdeps PKG_MNGR=$(CENTOS_PKG) OS=rpm

	# Download and install Docker
	sudo yum-config-manager -y --add-repo https://download.docker.com/linux/centos/docker-ce.repo
	$(MAKE) dockerdeps PKG_MNGR=$(CENTOS_PKG)

	# Install Python 3
	sudo $(CENTOS_PKG) install -y $(PYTHON3_DEPS)

	# Update if needed
	sudo $(CENTOS_PKG) update -y

dockerdeps:

	if [[ `command -v docker` == '' ]]; then \
		sudo $(PKG_MNGR) install -y $(DOCKER_DEPS); \
	fi

	docker --version
	node --version

npmdeps:

	if [[ `command -v npm` == '' ]]; then \
		sudo $(PKG_MNGR) install -y node-gyp libssl1.0-dev; \
		sudo $(PKG_MNGR) install -y npm; \
	fi

	npm install
	npm --version

.PHONY: pythondeps
pythondeps:
	pip3 -q install --upgrade pip setuptools
	pip3 -q install -r requirements.txt

.PHONY: devdeps
devdeps:
	@echo "Installing test dependencies"
	@echo "----------------------------"
	pip3 -q install -r dev-requirements.txt -r doc-requirements.txt
	if [ -f "/etc/lsb-release" ]; then \
		sudo apt-get -qq install phantomjs; \
	elif [ -f "/etc/centos-release" ]; then \
		curl -O https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2; \
		tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2 -C /usr/local/share; \
		sudo ln -s /usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin; \
	fi

	# Install geckodriver (for selenium testing)
	curl -L -O https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz
	sudo sh -c 'tar -x geckodriver -zf geckodriver-v0.26.0-linux64.tar.gz -O > /usr/bin/geckodriver'
	sudo chmod +x /usr/bin/geckodriver
	rm geckodriver-v0.26.0-linux64.tar.gz

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
	bash scripts/generate_certificate.sh $(CERT_TYPE) $(SIMPHONY_REMOTE); \

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
		docker pull simphonyproject/simphonic-paraview:latest; \
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


