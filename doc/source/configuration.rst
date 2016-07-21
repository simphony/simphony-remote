Configuration
=============

Configure the spawner
---------------------

The jupyterhub configuration is documented in the `jupyterhub documentation
<https://jupyterhub.readthedocs.io/en/latest/getting-started.html>`_. The
important difference is the spawner to use, which is configured as::

    c.JupyterHub.spawner_class = 'remoteappmanager.spawner.Spawner'

in the `jupyterhub_config.py` file.


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
   all the command line options are filled in, with the config file path
   default to `remoteappmanager_config.py` in the current directory.

   It is possible to change this location by specifying::

     c.Spawner.config_file_path = "/path/to/config.py"

in the `jupyterhub_config.py` file. Note that this config file will be used by
all remoteappmanagers for any user.


2. Config file

   The config file is referred to by the `--config-file-path` command line
   option. It is a Python file in which default values of attributes in
   :py:class:`remoteappmanager.file_config.FileConfig` can be override.

   For example, to use CSV as the database, one could provide a config file
   with the following setting::

     accounting_class = 'remoteappmanager.db.csv_db.CSVAccounting'
     accounting_kwargs = {'url': '/path/to/csv_file'}

   Please refer to :py:class:`remoteappmanager.file_config.FileConfig` for
   the configurable parameters.
