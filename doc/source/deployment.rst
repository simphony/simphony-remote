Deployment
==========

Single Machine
--------------

Deployment of the complete system in a single machine/VM.

.. note::

   The following instructions assume a clean up-to-date ubuntu 14.04
   system.

#. Retrieve the single user session manager::

     git clone https://github.com/simphony/simphony-remote

#. Create and activate a virtual environment::

     make venv
     . venv/bin/activate 

#. Install apt dependencies. You need to be root to execute this::

     make aptdeps

#. Install python dependencies::

     make pythondeps

#. Generate the SSL certificates if you do not already have them. The
   resulting certificates will have names test.* because they are
   self-signed and **are not supposed to be used for production**.
   A CA-signed certificate should be obtained instead.
   The certificates will be created in the jupyterhub directory::

     make certs

#. Create the database. By default, this is a sqlite file::

     make db

#. Change dir into jupyterhub::

     cd ../jupyterhub

   and verify that `jupyterhub_config.py` and `remoteappmanager_config.py` are
   correct for your deployment machine setup.

Setup docker containers
-----------------------

Compatible docker containers can be found in DockerHub. Refer to the documentation
of `simphony-remote-docker <https://github.com/simphony/simphony-remote-docker>`_ 
repository to deploy the images.

Once installed, use the `remoteappdb` program to create users, applications,
and authorize users to start applications. Refer to the :ref:`utilities`
section for details on the use of this program.

Start JupyterHub
----------------

#. Start jupyterhub by invoking the start script::

     sh start.sh

   .. note::
      If you want to keep the application running, use screen to start
      a detachable terminal.

   .. note::
      Running on OSX or with a separate docker machine requires that the
      appropriate environment variables are set before starting jupyterhub.
      refer to the command `docker-machine env` to setup the appropriate
      environment. In general, invoking::

            eval `docker-machine env`

      will enable the appropriate environment.
      On Linux, by default the host machine and the docker machine coincide,
      so this step is not needed.

#. JupyterHub is now running at https://localhost:8000
