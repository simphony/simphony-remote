import importlib

from remoteappmanager.handlers.handler_authenticator import HubAuthenticator
from traitlets import Instance, default
from tornado import web, gen
import tornado.ioloop
from jinja2 import Environment, FileSystemLoader

from tornadowebapi.registry import Registry

from remoteappmanager.db.interfaces import ABCAccounting
from remoteappmanager.logging.logging_mixin import LoggingMixin
from remoteappmanager.docker.container_manager import ContainerManager
from remoteappmanager.jinja2_adapters import Jinja2LoaderAdapter, gravatar_id
from remoteappmanager.user import User
from remoteappmanager.traitlets import as_dict
from remoteappmanager.services.hub import Hub
from remoteappmanager.services.reverse_proxy import ReverseProxy


class BaseApplication(web.Application, LoggingMixin):
    """Base application provides the common infrastructure
    to our tornado applications.
    Derived classes generally override _webapi_resources() and
    _web_handlers().
    """

    #: The user currently obtained from the command line. It
    #: is well established at startup and passed to the request
    #: handler _only_ when authencation is passed, otherwise Null
    #: will be passed.
    user = Instance(User)

    #: An accounting system that knows the allowed users, what applications
    #: they can run etc.
    db = Instance(ABCAccounting, allow_none=True)

    #: API access to the configurable-http-proxy
    reverse_proxy = Instance(ReverseProxy)

    #: API access to jupyterhub (for auth requests)
    hub = Instance(Hub)

    #: Manages the docker interface
    container_manager = Instance(ContainerManager)

    #: The WebAPI registry for resources.
    registry = Instance(Registry)

    @property
    def command_line_config(self):
        return self._command_line_config

    @property
    def file_config(self):
        return self._file_config

    @property
    def environment_config(self):
        return self._environment_config

    def __init__(self,
                 command_line_config,
                 file_config,
                 environment_config):
        """Initializes the application

        config: ApplicationConfiguration
            The application configuration object
        """

        self._command_line_config = command_line_config
        self._file_config = file_config
        self._environment_config = environment_config

        # Observe that settings and config are different things.
        # Config is the external configuration we can change.
        # settings is what we pass as a dictionary to tornado.
        # As a result, settings can contain more information than
        # config.
        settings = {}
        settings.update(as_dict(command_line_config))
        settings.update(as_dict(file_config))
        settings["static_url_prefix"] = (
            self._command_line_config.base_urlpath + "static/")

        self._jinja_init(settings)

        handlers = self._get_handlers()

        super().__init__(handlers, **settings)

    # Initializers
    @default("container_manager")
    def _container_manager_default(self):
        """Initializes the docker container manager."""
        return ContainerManager(
            realm=self.file_config.docker_realm,
            docker_config=self.file_config.docker_config()
        )

    @default("reverse_proxy")
    def _reverse_proxy_default(self):
        """Initializes the reverse proxy connection object."""
        # Note, we use jupyterhub orm Proxy, but not for database access,
        # just for interface convenience.
        return ReverseProxy(
            endpoint_url=self.command_line_config.proxy_api_url,
            api_token=self.environment_config.proxy_api_token,
        )

    @default("hub")
    def _hub_default(self):
        """Initializes the Hub instance."""
        return Hub(endpoint_url=self.command_line_config.hub_api_url,
                   api_token=self.environment_config.jpy_api_token,
                   )

    @default("db")
    def _db_default(self):
        """Initializes the database connection."""
        class_path = self.file_config.accounting_class
        module_path, _, cls_name = class_path.rpartition('.')
        cls = getattr(importlib.import_module(module_path), cls_name)
        try:
            return cls(**self.file_config.accounting_kwargs)
        except Exception:
            reason = 'The database is not initialised properly.'
            self.log.exception(reason)
            raise web.HTTPError(reason=reason)

    @default("user")
    def _user_default(self):
        """Initializes the user at the database level."""
        user_name = self.command_line_config.user
        user = User(name=user_name)
        user.account = self.db.get_user(user_name=user_name)
        return user

    @default("registry")
    def _registry_default(self):
        reg = Registry()
        reg.authenticator = HubAuthenticator
        for resource_class in self._webapi_resources():
            reg.register(resource_class)
        return reg

    # Public

    def start(self):
        """Start the application and the ioloop"""
        self.log.info("Starting server with options:")

        for trait_name in self._command_line_config.trait_names():
            self.log.info("{}: {}".format(
                trait_name,
                getattr(self._command_line_config, trait_name))
            )

        loop = tornado.ioloop.IOLoop.current()
        loop.add_callback(self._start_async)
        try:
            loop.start()
        except KeyboardInterrupt:
            print("\nInterrupted")

    # Private
    @gen.coroutine
    def _start_async(self):
        """Does initial setup and starts the server."""
        yield self._sync_reverse_proxy_with_docker_state()

        self.log.info("Listening for connections on {}:{}".format(
            self.command_line_config.ip,
            self.command_line_config.port))

        self.listen(self.command_line_config.port)

    @gen.coroutine
    def _sync_reverse_proxy_with_docker_state(self):
        """Executed when this server starts up.
        Verifies the current state of the docker containers that are
        running and submits them to the reverse proxy.
        The reason is that the reverse proxy might have died in the
        meantime, losing all its state, and we need to reinject this
        state so that it redirects to the containers that are under
        our control.
        """

        self.log.info("Re-registering running containers on the reverse proxy")
        containers = yield self.container_manager.running_containers_for_user(
            self.user.name)

        for container in containers:
            try:
                yield self.reverse_proxy.register(
                    container.urlpath,
                    container.host_url)
            except Exception:
                self.log.exception("Unable to register on the reverse proxy")

    def _webapi_resources(self):
        """Return a list of resources to be exported by the Web API.
        Reimplement this in subclasses to export specific resources"""
        return []

    def _web_handlers(self):
        """Return a list of handlers in tornado format (url, handler).
        Reimplement this in subclasses to export the specified endpoints"""
        return []

    def _get_handlers(self):
        """Returns the registered handlers"""
        base_urlpath = self.command_line_config.base_urlpath
        web_api = self.registry.api_handlers(base_urlpath)
        web_handlers = self._web_handlers()
        return web_api+web_handlers

    def _jinja_init(self, settings):
        """Initializes the jinja template system settings.
        These will be passed as settings and will be accessible at
        rendering."""
        jinja_env = Environment(
            loader=FileSystemLoader(
                settings["template_path"]
            ),
            autoescape=True,
        )

        jinja_env.filters["gravatar_id"] = gravatar_id
        settings["template_loader"] = Jinja2LoaderAdapter(jinja_env)
