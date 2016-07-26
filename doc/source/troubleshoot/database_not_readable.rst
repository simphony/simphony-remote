The database is not initalised
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each user's server requires a database setup and readable by the local process on which the :py:mod:`remoteappmanager` web application is started.  The error message indicates that the database is not readable (e.g. it does not exist).  Please refer to :ref:`deploy_setup_db` for details and options on setting up the database.

For more details on how the local process is managed, please refers to :py:mod:`remoteappmanager.spawner`.
