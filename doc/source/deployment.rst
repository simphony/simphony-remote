Deployment
==========

Single Machine
--------------

Deployment of the complete system in a single machine/VM.

.. note::

   The following instructions assume a clean up-to-date Ubuntu 18.04 or CentOS 7
   system with ``git`` and ``make`` installed.

#. Retrieve the required repository::

     git clone https://github.com/simphony/simphony-remote.git

#. Make sure that you have a recent version of Docker. This guide has been tested on version 19.03.5 (build 633a0ea838).
   :code:`make deps` will install the latest version if you do not already have a version of docker available.
   Full instructions available at `the Docker website <https://docs.docker.com/engine/installation/linux/ubuntulinux/>`_.
   A Makefile rule is provided for convenience.
   **NOTE: this overwrites the docker.list file you might have setup in your /etc/apt/sources.d/ directory**.
   You might be prompted for the root password to execute this::

     make deps

#. Make sure your docker server is running, and your user is allowed to connect to
   the docker server (check accessibility of `/var/run/docker.sock`). You obtain this by
   running::

     sudo service docker start
     sudo addgroup your_username docker

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

#. Change dir into jupyterhub::

     cd ./jupyterhub

   and verify that `jupyterhub_config.py` is correct for your deployment
   machine setup (see :ref:`configuration`).

#. If you are using virtual users (users that are not present on the system) you need to create
   a temporary space where the virtual user homes are created::

     mkdir /tmp/remoteapp

#. You can now start the service::

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

    Currently, the only fully supported browser is Google Chrome/Chromium. The latest version of Firefox has shown
    some issues with keyboard input when the vnc is running, however for the most part users will likley not
    suffer any issues.

#. Visit the site at::

    https://127.0.0.1:8000

   For many browsers this must be typed exactly as shown - using http://127.0.0.1:8000 or localhost:8000
   will not work. As mentioned above, the self-signed SSL certificates should cause your browser to 
   raise a warning and require adding 127.0.0.1 to the list of security exceptions.  

Setup docker containers
-----------------------

To create new images, please follow the documentation hosted at Horizon 2020
`Simphony <https://github.com/simphony/simphony-remote-docker>`_ project repository.


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

Using Nginx Reverse Proxy
=========================

Although the SimPhoNy-Remote installation will include ``nginx``, it is up to the developer to make sure that it is
running correctly, with ``http`` and ``https`` firewall access also set up.

To begin with, please first ensure that the following directories exist in your file system (you will need root
privileges in order to do so)::

  /etc/ssl/certs/
  /etc/ssl/private/
  /etc/nginx/conf.d/

If you want to use self-signed certificates, you can run the following ``make`` command in order to generate a more
secure set of RSA certificates and Diffie-Helman parameters for the Nginx reverse proxy::

  make certs CERT_TYPE='nginx'
  sudo mv nginx/certs/nginx-selfsigned.key /etc/ssl/private/
  sudo mv nginx/certs/nginx-selfsigned.crt /etc/ssl/certs/
  sudo mv nginx/certs/dhparam.pem /etc/ssl/certs/

Then edit the ``nginx/nginx.conf.template`` file provided will in order to include a public IP address / server name
in the sections marked ``<external server name>``. If you prefer to use authenticated certificates this is also the
time to edit the ``ssl_certificate`` and ``ssl_certificate_key`` sections with the updated locations of these files.

The Nginx template file will need to be copied into the following location (and given the ``.conf`` extension) in
order to be discoverable by the ``nginx`` proxy::

  sudo cp nginx/nginx.conf.template /etc/nginx/conf.d/sr-nginx.conf

After restarting the ``nginx`` service to make sure the new configuration is applied, run SimPhoNy-Remote as normal
and it will be discoverable at https://<external_server_name>

Running as a Service
====================

Instructions for how to run a general JupyterHub deployment as a service can be found
`here <https://github.com/jupyterhub/jupyterhub/wiki/Run-jupyterhub-as-a-system-service>`_.

Instead of executing a ``jupyterhub <config.py> <flags>`` command upon starting the service, it is
more advisable to call ``bash <simphony-remote>/jupterhub/start.sh`` instead.
