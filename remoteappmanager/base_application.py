import importlib
from secrets import token_urlsafe

from traitlets import Instance, default
from tornado import web, gen
import tornado.ioloop

from jupyterhub._version import __version__, _check_version
from tornado.httpclient import AsyncHTTPClient
from tornadowebapi.registry import Registry
from tornado.web import RequestHandler

from remoteappmanager.db.interfaces import ABCDatabase
from remoteappmanager.logging.logging_mixin import LoggingMixin
from remoteappmanager.docker.container_manager import ContainerManager
from remoteappmanager.handlers.handler_authenticator import HubAuthenticator
from remoteappmanager.user import User
from remoteappmanager.traitlets import as_dict
from remoteappmanager.services.hub import Hub
from remoteappmanager.services.reverse_proxy import ReverseProxy


DEFAULT_POLICY_OPTIONS = {
    "app_license": None,
    "allow_home": False,
    "allow_view": True,
    "volume": None,
    "allow_startup_data": False
}


class BaseApplication(web.Application, LoggingMixin):
    """Base application provides the common infrastructure
    to our tornado applications.
    Derived classes generally override _webapi_resources() and
    _web_handlers().
    """

    #: The user currently obtained from the command line. It
    #: is well established at startup and passed to the request
    #: handler _only_ when authentication is passed, otherwise Null
    #: will be passed.
    user = Instance(User)

    #: An accounting system that knows the allowed users, what applications
    #: they can run etc.
    db = Instance(ABCDatabase, allow_none=True)

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
        settings['X-JupyterHub-Version'] = __version__

        # Since we are using JupyterHub as an OAuth provider we'll also
        # need to create our own cookies to keep track of user logins
        settings['cookie_secret'] = token_urlsafe(64)

        handlers = self._get_handlers()

        super().__init__(handlers, **settings)
        self.patch_default_headers()

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
        """Initializes the Hub instance used to authenticate with
        JupyterHub.
        """
        return Hub(
            endpoint_url=self.environment_config.hub_api_url,
            api_token=self.environment_config.jpy_api_token,
            base_url=self.command_line_config.base_urlpath,
            hub_prefix=self.command_line_config.hub_prefix,
        )

    @default("db")
    def _db_default(self):
        """Initializes the database connection."""
        class_path = self.file_config.database_class
        module_path, _, cls_name = class_path.rpartition('.')
        cls = getattr(importlib.import_module(module_path), cls_name)
        try:
            return cls(**self.file_config.database_kwargs)
        except Exception:
            reason = 'The database is not initialised properly.'
            self.log.exception(reason)
            raise web.HTTPError(reason=reason)

    @default("user")
    def _user_default(self):
        """Initializes the user at the database level."""
        user_name = self.command_line_config.user
        login_service = self.command_line_config.login_service
        user = User(name=user_name, login_service=login_service)

        # Handle User accounting
        if self.db.get_user(user_name=user.name) is None:
            self.log.info(
                "User account not found for {}:".format(user.name))
            if self.file_config.auto_user_creation:
                self.log.info(
                    "Creating new User account for {}:".format(user.name))
                self.db.create_user(user.name)
        else:
            self.log.info("User account found for {}:".format(user.name))
        user.account = self.db.get_user(user_name=user.name)

        # Add any demo apps to registry
        self.log.info("Adding demo apps to User registry:")
        self._add_demo_apps(user)

        return user

    @default("registry")
    def _registry_default(self):
        reg = Registry()
        reg.authenticator = HubAuthenticator
        for resource_handler in self._webapi_resources():
            reg.register(resource_handler)
        return reg

    # Public
    def start(self):
        """Start the application and the ioloop"""
        self.log.info("Starting SimPhoNy-Remote using JupyterHub"
                      " server version %s", __version__)
        self.log.info("Starting server with options:")
        for trait_name in self._command_line_config.trait_names():
            self.log.info("{}: {}".format(
                trait_name,
                getattr(self._command_line_config, trait_name)
                )
            )
        for trait_name in self._environment_config.trait_names():
            self.log.info("{}: {}".format(
                trait_name,
                getattr(self._environment_config, trait_name)
            )
            )
        self.log.info("Listening for connections on {}:{}".format(
            self.command_line_config.ip,
            self.command_line_config.port))

        self.listen(self.command_line_config.port)

        tornado.ioloop.IOLoop.current().run_sync(self.check_hub_version)
        tornado.ioloop.IOLoop.current().start()

    @gen.coroutine
    def check_hub_version(self):
        """Test a connection to the JupyterHub warn on sufficient
        mismatch between versions
        """
        client = AsyncHTTPClient()
        RETRIES = 5
        for i in range(1, RETRIES + 1):
            try:
                resp = yield client.fetch(
                    self.environment_config.hub_api_url)
            except Exception:
                self.log.exception(
                    "Failed to connect to my Hub at %s (attempt %i/%i)."
                    " Is it running?",
                    self.environment_config.hub_api_url, i, RETRIES)
                yield gen.sleep(min(2 ** i, 16))
            else:
                break
        else:
            self.exit(1)

        hub_version = resp.headers.get('X-JupyterHub-Version')
        _check_version(hub_version, __version__, self.log)

    def patch_default_headers(self):
        """Ensure the current JupyterHub version has been added to
        each request handler header, since this will be checked for
        compatibility by the hub
        """
        if hasattr(RequestHandler, '_orig_set_default_headers'):
            return
        RequestHandler._orig_set_default_headers = RequestHandler.set_default_headers  # noqa: E501

        def set_jupyterhub_header(self):
            self._orig_set_default_headers()
            self.set_header('X-JupyterHub-Version', __version__)

        RequestHandler.set_default_headers = set_jupyterhub_header

    # Private
    def _add_demo_apps(self, user):
        """Grant access to any demo applications provided for user"""
        if user.account is None:
            self.log.debug("No user account available")
            return

        if not self.file_config.demo_applications:
            self.log.debug("No demo applications available")
            return

        # Add all demo applications already registered
        for application in self.db.list_applications():
            if application.image in self.file_config.demo_applications:
                self.log.debug(f"Available image: {application.image}")
                options = DEFAULT_POLICY_OPTIONS.copy()
                options.update(
                    self.file_config.demo_applications[application.image])
                self.db.grant_access(
                    app_name=application.image,
                    user_name=user.name,
                    **options
                )

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
        # Must include callback handlers to complete OAuth flow
        web_auth = self.hub.callback_handlers()
        web_api = self.registry.api_handlers(base_urlpath)
        web_handlers = self._web_handlers()
        return web_auth+web_api+web_handlers
