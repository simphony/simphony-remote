Configuration
=============

Of the spawner
--------------

The jupyterhub configuration is documented in the `jupyterhub documentation
<https://jupyterhub.readthedocs.io/en/latest/getting-started.html>`_. The
important difference is the spawner to use, which is configured as::

    c.JupyterHub.spawner_class = 'remoteappmanager.spawner.Spawner'


Of the remoteappmanager
-----------------------

Configuration of the remote application is performed from two sources.

- the command line, specified by the Spawner.
- a config file (normally `remoteappmanager_config.py`). The location of this
  file is specified as part of the command line options.

Their options are fully disjoint, and they configure different aspects
of the application: command line options are dynamically decided according to
the user that requests the spawn; Config file options are general in nature,
and allow the remoteappmanager to perform adequately against the current
docker setup.

By default, the spawner passes the `remoteappmanager_config.py` in the
directory where jupyterhub was started. It is possible to change this location
by specifying::

    c.Spawner.config_file_path = "/path/to/config.py"

in the `jupyterhub_config.py` file. Note that this config file will be used by
all remoteappmanagers for any user.
