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


Setup Database Accounting
-------------------------

A database is needed for managing the remote applications available for each user.
Note that this database is in addition to the database created or used by JupyterHub.

Various accounting sources are supported:

1. Default sqlite database

   **remoteappmanager** by default uses a sqlite database *remoteappmanager.db* in
   the current work directory.  The **remoteappdb** command-line tool is provided
   for setting up the database.  Please refer to the :ref:`utilities`
   section for details on the use of this program.

2. Other DBAPI_ implementations and databases

   For database implementation supported by SQLAlchemy_, you may configure
   **remoteappmanager** to use :py:class:`remoteappmanager.db.orm.AppAccounting`.
   Please also refer to :ref:`config_remoteappmanager` for details on setting
   up the accounting class.

   .. note::
      The use of databases other than sqlite3 is not tested

3. CSV file

   You may configurate **remoteappmanager** to use a CSV file as its database.
   Please refer to :ref:`config_remoteappmanager` for details on setting up
   the accounting class to use :py:class:`remoteappmanager.db.csv_db.CSVAccounting`.

4. Others

   Any arbitrary database implementation may be used as long as an accounting
   class compliant to the API of :py:class:`remoteappmanager.db.interfaces.ABCAccounting`
   is provided. Please also refer to :ref:`config_remoteappmanager` for details
   on setting up the accounting class.


.. _SQLAlchemy: http://docs.sqlalchemy.org/en/latest/index.html
.. _DBAPI: https://www.python.org/dev/peps/pep-0249/



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
