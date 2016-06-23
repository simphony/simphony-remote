import sys

import os
from sqlalchemy.orm.exc import MultipleResultsFound
from tornado import web, gen
from urllib import parse
import tornado.ioloop

from jinja2 import Environment, FileSystemLoader
from jupyterhub import orm as jupyterhub_orm

from remoteappmanager.db import orm
from remoteappmanager.handlers.api import HomeHandler
from remoteappmanager.logging.logging_mixin import LoggingMixin
from remoteappmanager.docker.container_manager import ContainerManager
from remoteappmanager.docker.docker_client_config import DockerClientConfig
from remoteappmanager.jinja2_adapters import Jinja2LoaderAdapter


class Application(web.Application, LoggingMixin):
    """Tornado main application"""

    def __init__(self, config):
        """Initializes the application

        config: ApplicationConfiguration
            The application configuration object
        """

        self._config = config

        # Observe that settings and config are different things.
        # Config is the external configuration we can change.
        # settings is what we pass as a dictionary to tornado.
        # As a result, settings can contain more information than
        # config.
        settings = {}
        settings.update(config.as_dict())
        settings["static_url_prefix"] = self._config.base_url+"static/"

        self._db_init()
        self._jinja_init(settings)
        self._container_manager_init()
        self._reverse_proxy_init()
        self._user_init()

        handlers = self._get_handlers()

        super().__init__(handlers, **settings)

    @property
    def config(self):
        return self._config

    def start(self):
        """Start the application and the ioloop"""

        self.log.info("Starting server with options:")
        for trait_name in self._config.trait_names():
            self.log.info("{}: {}".format(
                trait_name,
                getattr(self._config, trait_name)
                )
            )
        self.log.info("Listening for connections on {}:{}".format(
            self.config.ip,
            self.config.port))

        self.listen(self.config.port)

        tornado.ioloop.IOLoop.current().start()

    def container_url_abspath(self, container):
        """Returns the absolute path of a container, considering the
        application setup.

        Parameters
        ----------
        container : Container
            A container object.

        Returns
        -------
        The absolute path part of the url.
        """
        return self.config.base_url + container.url

    @gen.coroutine
    def reverse_proxy_remove_container(self, container):
        """Removes a container from the reverse proxy at the associated url.

        Parameters
        ----------
        container : Container
            A container object.
        """
        proxy = self.reverse_proxy

        container_url = self.container_url_abspath(container)
        self.log.info("Deregistering url {} to {} on reverse proxy.".format(
            container_url,
            container.host_url
        ))

        yield proxy.api_request(container_url, method='DELETE')

    @gen.coroutine
    def reverse_proxy_add_container(self, container):
        """Adds the url associated to a given container on the reverse proxy.

        Parameters
        ----------
        container : Container
            A container object.
        """

        proxy = self.reverse_proxy
        container_url_path = self.container_url_abspath(container)

        self.log.info("Registering url {} to {} on reverse proxy.".format(
            container_url_path,
            container.host_url
        ))

        yield proxy.api_request(
            container_url_path,
            method='POST',
            body=dict(
                target=container.host_url,
            )
        )

    # Private
    def _get_handlers(self):
        """Returns the registered handlers"""

        return [
            (self._config.base_url, HomeHandler),
            (self._config.base_url.rstrip('/'),
             web.RedirectHandler, {"url": self._config.base_url}),
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

    def _container_manager_init(self):
        """Initializes the docker container manager."""

        self.container_manager = ContainerManager(
            docker_config=DockerClientConfig(
                tls=self._config.tls,
                tls_verify=self._config.tls_verify,
                tls_ca=self._config.tls_ca,
                tls_key=self._config.tls_key,
                tls_cert=self._config.tls_cert,
                docker_host=self._config.docker_host,
            )
        )

    def _reverse_proxy_init(self):
        """Initializes the reverse proxy connection object."""
        try:
            auth_token = os.environ["PROXY_API_TOKEN"]
        except KeyError:
            self.log.error("Cannot extract PROXY_API_TOKEN to initialise the "
                           "reverse proxy connection. Exiting.")
            raise

        # Note, we use jupyterhub orm Proxy, but not for database access,
        # just for interface convenience.
        self.reverse_proxy = jupyterhub_orm.Proxy(
            auth_token=auth_token,
            api_server=_server_from_url(self._config.proxy_api_url)
        )

        self.log.info("Reverse proxy setup on {}".format(
            self._config.proxy_api_url
        ))

    def _db_init(self):
        """Initializes the database connection."""
        self.db = orm.Database(self.config.db_url)

    def _user_init(self):
        Session = self.db.create_session_factory()

        session = Session()
        try:
            user = session.query(orm.User).filter(
                name=self.config.user).one_or_none()
        except MultipleResultsFound:
            self.log.error("Multiple results found when "
                           "querying for username {}. This is supposedly "
                           "impossible because the username should be a "
                           "unique key by design.".format(self.config.user))
            # This is pretty much an unrecoverable error and we should give up
            sys.exit(1)

        if user is None:
            user = orm.User(name=self.config.user)
            user.teams.append(user)
            session.add(self.user)

        # make sure that the user always has at least one team: his own.

        if len(user.teams) == 0:
            team = orm.Team(name=self.config.user)
            self.user.teams.append(team)
            session.add(team)

        session.commit()

        self.user = user


def _server_from_url(url):
    """Creates a orm.Server from a given url"""
    parsed = parse.urlparse(url)
    return jupyterhub_orm.server(
        proto=parsed.scheme,
        ip=parsed.hostname,
        port=parsed.port,
        base_url=parsed.path
    )
