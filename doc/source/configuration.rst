.. _configuration:

Configuration
=============

Configure the spawner
---------------------

The jupyterhub configuration is documented in the `jupyterhub documentation
<https://jupyterhub.readthedocs.io/en/latest/getting-started.html>`_. The
important difference is the spawner to use, which is configured as::

    c.JupyterHub.spawner_class = 'remoteappmanager.jupyterhub.spawners.SystemUserSpawner'
    # or
    # c.JupyterHub.spawner_class = 'remoteappmanager.jupyterhub.spawners.VirtualUserSpawner'

in the `jupyterhub_config.py` file.

Please refer to :py:mod:`remoteappmanager.jupyterhub.spawners` for the available spawners
in this project.


Configure the authenticator and the admin user
----------------------------------------------

Different authenticators can be plugged into jupyterhub. In the configuration
file, the following entry will change the authenticator::

     c.JupyterHub.authenticator_class = ('remoteappmanager.jupyterhub.auth.WorldAuthenticator')

`WorldAuthenticator` will allow any user to pass authentication. Use this
authenticator only for testing purposes.

Administration capabilities are decided by jupyterhub, not remoteappmanager.
`jupyterhub_config.py` allows to setup admin users with the following entry::

    c.Authenticator.admin_users = {"admin"}

Note that the entry must be a python set. Users in this set will, once logged
in, reach an administrative interface, instead of the docker application
management.

.. _config_remoteappmanager:

Configure the remoteappmanager
------------------------------

Configuration of the remote application is performed from two sources.

- the command line, specified by the Spawner.
- a config file. The location of this file is specified as part of the
  command line options.

Their options are fully disjoint, and they configure different aspects
of the application: Command line options are dynamically decided according to
the user that requests the spawn; Config file options are general in nature,
and allow the remoteappmanager to perform adequately against the current
docker setup.

1. Command line options

   .. literalinclude:: remoteappmanager_help.txt

   When **remoteappmanager** is started from jupyterhub using the spawner,
   all the command line options are filled in automatically.


2. Config file

   The **remoteappmanager** has a number of parameters configurable via a
   config file.  The path of the config file should be specified in the
   spawner in `jupyterhub_config.py`::

     c.SystemUserSpawner.config_file_path = "/path/to/config.py"

   Please refer to :py:class:`remoteappmanager.file_config.FileConfig` for
   the configurable parameters.  Note that this config file will be used
   by all remoteappmanagers for any user.

   For example, to use CSV as the database, `/path/to/config.py` would
   contain the followings::

     database_class = 'remoteappmanager.db.csv_db.CSVDatabase'
     database_kwargs = {'url': '/path/to/csv_file'}

