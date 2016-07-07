import os
<<<<<<< HEAD
from traitlets import Instance, default
from sqlalchemy.orm.exc import MultipleResultsFound
from tornado import web
=======
from urllib import parse

from traitlets import Instance
from tornado import web, gen
>>>>>>> master
import tornado.ioloop
from jinja2 import Environment, FileSystemLoader

from remoteappmanager.db import orm
from remoteappmanager.db.interfaces import ABCAccounting
from remoteappmanager.handlers.api import HomeHandler
from remoteappmanager.logging.logging_mixin import LoggingMixin
from remoteappmanager.docker.container_manager import ContainerManager
from remoteappmanager.docker.docker_client_config import DockerClientConfig
from remoteappmanager.jinja2_adapters import Jinja2LoaderAdapter
from remoteappmanager.user import User
from remoteappmanager.traitlets import as_dict
from remoteappmanager.services.hub import Hub
from remoteappmanager.services.reverse_proxy import ReverseProxy


class Application(web.Application, LoggingMixin):
    """Tornado main application"""

    user = Instance(User)

    db = Instance(ABCAccounting, allow_none=True)

    reverse_proxy = Instance(ReverseProxy)

    hub = Instance(Hub)

    container_manager = Instance(ContainerManager)

    def __init__(self,
                 command_line_config,
                 file_config):
        """Initializes the application

        config: ApplicationConfiguration
            The application configuration object
        """

        self._command_line_config = command_line_config
        self._file_config = file_config

        # Observe that settings and config are different things.
        # Config is the external configuration we can change.
        # settings is what we pass as a dictionary to tornado.
        # As a result, settings can contain more information than
        # config.
        settings = {}
        settings.update(as_dict(command_line_config))
        settings.update(as_dict(file_config))
        settings["static_url_prefix"] = (
            self._command_line_config.base_url + "static/")

        self._jinja_init(settings)

        handlers = self._get_handlers()

        super().__init__(handlers, **settings)

    @property
    def command_line_config(self):
        return self._command_line_config

    @property
    def file_config(self):
        return self._file_config

    # Initializers
    @default("container_manager")
    def _container_manager_default(self):
        """Initializes the docker container manager."""

        return ContainerManager(
            docker_config=DockerClientConfig(
                tls=self.file_config.tls,
                tls_verify=self.file_config.tls_verify,
                tls_ca=self.file_config.tls_ca,
                tls_key=self.file_config.tls_key,
                tls_cert=self.file_config.tls_cert,
                docker_host=self.file_config.docker_host,
            )
        )

    @default("reverse_proxy")
    def _reverse_proxy_default(self):
        """Initializes the reverse proxy connection object."""
        try:
            auth_token = os.environ["PROXY_API_TOKEN"]
        except KeyError:
            self.log.error("Cannot extract PROXY_API_TOKEN to initialise the "
                           "reverse proxy connection. Exiting.")
            raise

        # Note, we use jupyterhub orm Proxy, but not for database access,
        # just for interface convenience.
        return ReverseProxy(
            endpoint_url=self.command_line_config.proxy_api_url,
            auth_token=auth_token)

    @default("hub")
    def _hub_default(self):
        """Initializes the Hub instance."""
        return Hub(endpoint_url=self.command_line_config.hub_api_url,
                   api_key=os.environ.get('JPY_API_TOKEN', "")
                   )

    @default("db")
    def _db_default(self):
        """Initializes the database connection."""
        return orm.AppAccounting(self.file_config.db_url)

    @default("user")
    def _user_default(self):
        """Initializes the user at the database level."""
        user_name = self.command_line_config.user
        user = User(name=user_name)
        user.orm_user = self.db.get_user_by_name(user_name)
        return user

    # Public
    def start(self):
        """Start the application and the ioloop"""

        self.log.info("Starting server with options:")
        for trait_name in self._command_line_config.trait_names():
            self.log.info("{}: {}".format(
                trait_name,
                getattr(self._command_line_config, trait_name)
                )
            )
        self.log.info("Listening for connections on {}:{}".format(
            self.command_line_config.ip,
            self.command_line_config.port))

        self.listen(self.command_line_config.port)

        tornado.ioloop.IOLoop.current().start()

    # Private
    def _get_handlers(self):
        """Returns the registered handlers"""

        base_url = self.command_line_config.base_url
        return [
            (base_url, HomeHandler),
            (base_url.rstrip('/'),
             web.RedirectHandler, {"url": base_url}),
        ]

    def _jinja_init(self, settings):
        """Initializes the jinja template system settings.
        These will be passed as settings and will be accessible at
        rendering."""
        jinja_env = Environment(
            loader=FileSystemLoader(
                settings["template_path"]
            ),
            autoescape=True
        )

        settings["template_loader"] = Jinja2LoaderAdapter(jinja_env)
