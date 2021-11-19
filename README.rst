Simphony-remote
===============

.. image:: https://readthedocs.org/projects/simphony-remote/badge/?version=latest
   :target: http://simphony-remote.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

The Simphony-remote is web service that allows users to start and work with simphony enabled environments remotely.

Key provided features:

   - Isolated working environments using docker containers.
   - No install remote access through a web browser.
   - Sharing of working sessions.
   - Based on community supported open source initiatives (JupyterHub)

Acknowledgments
---------------

This software is developed under the SimPhoNy project, an EU-project
funded by the 7th Framework Programme (Project number 604005) under
the call NMP.2013.1.4-1: "Development of an integrated multi-scale
modelling environment for nanomaterials and systems by design".

Documentation
=============

A quick setup guide is given below; please see the `documentation <doc/source/index.rst>`_ for more
detailed information.

Deployment (Quick Start)
========================

Basic instructions for a single-user deployment on a local (or virtual) machine are provided below.
A more comprehensive deployment documentation, including use of a ``nginx`` reverse proxy and
running as a service can be found `here <doc/source/deployment.rst>`_

Single Machine
--------------

If you would like to test a deployment of S-R using Docker for CI purposes, then please use the following
`instructions <doc/source/developer/ci_instructions.rst>`_.

.. note::

   The following instructions assume a clean up-to-date Ubuntu 18.04 or CentOS 7
   system with ``git`` and ``make`` installed.

#. Retrieve the required repository::

     git clone https://github.com/simphony/simphony-remote.git

#. Make sure that you have a recent version of Docker. This guide has been tested on version 19.03.5 (build 633a0ea838).
   :code:`make deps` will install the latest version if you do not already have a version of docker available.
   Full instructions available at the Docker website `for Ubuntu <https://docs.docker.com/engine/install/ubuntu/>`_
   and `for CentOS <https://docs.docker.com/engine/install/centos/>`_ operating systems.
   Docker installed using Ubuntu's Snap package manager might not work as expected; see
   https://github.com/simphony/simphony-remote/issues/572 for details.
   A Makefile rule is provided for convenience.
   **NOTE: this overwrites the docker.list file you might have setup in your /etc/apt/sources.d/ directory**.
   You might be prompted for the root password to execute this::

     make deps

#. Make sure your docker server is running, and your user is allowed to connect to
   the docker server (check accessibility of ``/var/run/docker.sock``). You obtain this by
   running::

     sudo service docker start

   followed by either::

    (Ubuntu) sudo addgroup your_username docker
    (CentOS) sudo groupmod -aG docker your_username

   and logging out and in again. Check if your docker server is operative by running::

     docker info

#. Create and activate a virtual environment, then set the appropriate PATH for the node modules::

     make venv
     . venv/bin/activate
     export PATH=`npm bin`:$PATH

#. Install the python dependencies::

     make pythondeps

#. And install the package itself::

     make install

#. Generate the SSL certificates if you do not already have them. The
   resulting certificates will have names test.* because they are
   self-signed and **are not supposed to be used for production**.
   A CA-signed certificate should be obtained instead.
   The certificates will be created in the jupyterhub directory::

     make certs

#. Create the database. By default, this is a sqlite file::

     make db

#. If you are using virtual users (users that are not present on the system) you need to create
   a temporary space where the virtual user homes are created::

     mkdir /tmp/remoteapp

The installation is complete, you can now start the service.

Start JupyterHub
----------------

#. Change dir into ``jupyterhub/``::

     cd ./jupyterhub

#. Verify that ``jupyterhub_config.py`` is correct for your deployment
   machine setup (see `configuration <doc/source/configuration>`_ for more details).
   Some example configuration files are provided in the
   ``example_configurations/`` directory.

#. Start JupyterHub by invoking the start script::

     bash start.sh

   .. note::
      If you want to keep the application running, use screen to start
      a detachable terminal.

   .. note::
      Running on OSX or with a separate docker machine requires that the
      appropriate environment variables are set before starting jupyterhub.
      refer to the command ``docker-machine env`` to setup the appropriate
      environment. In general, invoking::

            eval `docker-machine env`

      will enable the appropriate environment.
      On Linux, by default the host machine and the docker machine coincide,
      so this step is not needed.

#. JupyterHub is now running at https://127.0.0.1:8000

   For many browsers this must be typed exactly as shown - using http://127.0.0.1:8000 or localhost:8000
   will not work. As mentioned above, the self-signed SSL certificates should cause your browser to
   raise a warning and require adding 127.0.0.1 to the list of security exceptions.

   Currently, the only fully supported browser is Google Chrome/Chromium. The latest version of Firefox has shown
   some issues with keyboard input when the vnc is running, however for the most part users will likley not
   suffer any issues.

Setting up Docker images
------------------------

Next, we need to obtain a docker image to run on Simphony-Remote. This can be done by either pulling an existing
image from a docker registry, or creating our own locally.

To create new images, please follow the documentation hosted at Horizon 2020
`Simphony <https://github.com/simphony/simphony-remote-docker>`_ project repository.


Setup Database Accounting
-------------------------

A database is needed for managing the remote applications available for each user.
Note that this database is in addition to the database created or used by JupyterHub.

Default sqlite database

   **remoteappmanager** by default uses a sqlite database *remoteappmanager.db* in
   the current work directory.  The **remoteappdb** command-line tool is provided
   for setting up the database.  Please refer to the `utilities <doc/source/utilities.rst>`_
   section for details on the use of this program.


Setting up Users
----------------

Whilst Simphony-Remote is running using the standard ``jupyter_config.py`` script,
navigate to https://127.0.0.1:8000 in your browser and login with the username 'admin' and no password. Select the
'Users' tab on the left hand menu and click the 'Create New Entry' button in the top right. Make up a username and
click submit. 

Next, click the Applications tab in the left hand menu and click the 'Create New Entry' button in the top right.
We can add the name of any docker image available to the Docker daemon.

Then go back to the 'Users' tab, select the 'Policies' button next to the username. Create a new entry and choose
the added image name from the dropdown menu. Nothing else needs to be set, unless you want to mount a directory
within the docker container.

Log out of SimphonyRemote (red 'admin' button in the top right) and log in using the username you specified for your
new user and no password, you should now be able to start your application!
