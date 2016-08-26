.. _configuration:

Configuration
=============

Configure the spawner
---------------------

The jupyterhub configuration is documented in the `jupyterhub documentation
<https://jupyterhub.readthedocs.io/en/latest/getting-started.html>`_. The
important difference is the spawner to use, which is configured as::

    c.JupyterHub.spawner_class = 'remoteappmanager.spawners.SystemUserSpawner'
    # or
    # c.JupyterHub.spawner_class = 'remoteappmanager.spawners.VirtualUserSpawner'

in the `jupyterhub_config.py` file.

Please refer to :py:mod:`remoteappmanager.spawners` for the available spawners
in this project.


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

     accounting_class = 'remoteappmanager.db.csv_db.CSVAccounting'
     accounting_kwargs = {'url': '/path/to/csv_file'}

