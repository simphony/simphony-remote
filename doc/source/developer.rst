API reference
=============


RemoteAppManager
----------------

The main tornado web application that manages the containers (docker applications)
for each user.

.. autosummary::
   :toctree: api
   :template: module_template.rst

   remoteappmanager.application
   remoteappmanager.auth
   remoteappmanager.command_line_config
   remoteappmanager.file_config
   remoteappmanager.jinja2_adapters
   remoteappmanager.netutils
   remoteappmanager.spawners
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
   remoteappmanager.handlers.base_handler
   remoteappmanager.handlers.home_handler
   remoteappmanager.logging.logging_mixin
   remoteappmanager.restresources.application
   remoteappmanager.restresources.container
   remoteappmanager.services.hub
   remoteappmanager.services.reverse_proxy


REST tornado
------------

A generic implementation of Rest APIs using tornado.

.. autosummary::
   :toctree: api
   :template: module_template.rst

   remoteappmanager.rest.exceptions
   remoteappmanager.rest.registry
   remoteappmanager.rest.resource
   remoteappmanager.rest.rest_handler
   remoteappmanager.rest.http.payloaded_http_error

