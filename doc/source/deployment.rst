Deployment
==========

Single Machine
--------------

Deployment of the complete system in a single machine/VM.

.. note::

   The following instructions assume a clean up-to-date ubuntu 14.04
   system.

#. Install dependencies

::
  sudo apt-get install npm nodejs-legacy python3-pip python3.4-venv
  sudo npm install -g configurable-http-proxy

#. Install the single user session manager

::

   git clone https://github.com/simphony/simphony-remote

#. Create a venv, activate it::

     cd simphony-remote
     python3 -mvenv venv
     . venv/bin/activate
     pip3 install docker-py
     python3 setup.py install (or develop)


   .. note::
      Install docker-py with pip due to
      incorrect setup.py not handling python > 3.3

#. Generate the SSL certificates if you do not already have them. The
   resulting certificates will have names test.* because they are
   self-signed and **are not supposed to be used for production**.
   A CA-signed certificate should be obtained instead.
   You must choose and set a password of your liking, and use it when prompted.
   Additional information will also be requested, but are not strictly required
   and can be left as defaults.

   Once created the certificates, copy them to the jupyterhub directory::

     cd ../scripts
     sh generate_certificate.sh
     cp test.* ../jupyterhub/

#. Create the database. By default, this is a sqlite file::

     remoteappdb --db=~/remoteappmanager.db init

#. Change dir into jupyterhub::

     cd ../jupyterhub

   and verify that `jupyterhub_config.py` and `remoteappmanager_config.py` are
   correct for your deployment machine setup.

Setup docker containers
-----------------------

Compatible docker containers can be found in DockerHub

.. todo:: To be updated


Start JupyterHub
----------------

#. Start jupyterhub by invoking the start script::

     sh start.sh

   .. note::
      If you want to keep the application running, use screen to start
      a detachable terminal.

#. JupyterHub is now running at https://localhost:8000
