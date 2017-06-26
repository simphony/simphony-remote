Developer documentation
=======================

RemoteAppManager
----------------

The main tornado web application that manages the containers (docker applications)
for each user.

.. include::
    developer/docker.rst

API reference
-------------


.. autosummary::
   :toctree: api
   :template: module_template.rst

   remoteappmanager.application
   remoteappmanager.command_line_config
   remoteappmanager.file_config
   remoteappmanager.netutils
   remoteappmanager.traitlets
   remoteappmanager.user
   remoteappmanager.utils
   remoteappmanager.cli.remoteappdb.__main__
   remoteappmanager.cli.remoteapprest.__main__
   remoteappmanager.db.csv_db
   remoteappmanager.db.interfaces
   remoteappmanager.db.orm
   remoteappmanager.docker.async_docker_client
   remoteappmanager.docker.container
   remoteappmanager.docker.container_manager
   remoteappmanager.docker.image
   remoteappmanager.jupyterhub.auth
   remoteappmanager.jupyterhub.spawners
   remoteappmanager.handlers.base_handler
   remoteappmanager.handlers.user_home_handler
   remoteappmanager.logging.logging_mixin
   remoteappmanager.webapi.application
   remoteappmanager.webapi.container
   remoteappmanager.webapi.admin.application
   remoteappmanager.webapi.admin.container
   remoteappmanager.services.hub
   remoteappmanager.services.reverse_proxy
