import tornado.options
from remoteappmanager.utils import with_end_slash
from tornado.options import define, options
from traitlets import HasTraits, Int, Unicode, Bool

from remoteappmanager import paths


class ApplicationConfig(HasTraits):
    """Configuration options for the application server"""

    # Options that are available for configuration at the command line,
    # and are set by jupyterhub
    user = Unicode(
        help="The user as specified at the jupyterhub login",
        command_line=True)

    ip = Unicode(
        help="The IP address to bind",
        command_line=True)

    port = Int(
        help="Port at which to spawn",
        command_line=True)

    cookie_name = Unicode(
        help="The cookie name for authentication",
        command_line=True)

    # This is the url path that the user sees and which leads to this server.
    # typically, it's /user/username
    base_url = Unicode(
        help="The base url where the server resides",
        command_line=True)

    # This is the host of the hub. It's always empty (jupyterhub decision)
    hub_host = Unicode(
        help="The url of the jupyterhub server",
        command_line=True)

    # This is a url path that sends the request to jupyterhub.
    # It's normally /hub/
    hub_prefix = Unicode(
        help="The url prefix of the jupyterhub",
        command_line=True)

    # This is a full url to reach the hub api (e.g. for authentication check)
    hub_api_url = Unicode(
        help="The url of the jupyterhub REST API",
        command_line=True)

    # Authentication token for the hub api (e.g. for authentication check)
    # Should be passed as environment variable JPY_API_TOKEN
    hub_api_key = Unicode(
        help="The token for the jupyterhub REST API")

    # The full URL where to access the reverse proxy API.
    proxy_api_url = Unicode(
        help="The url of the reverse proxy API",
        command_line=True
    )

    config_file = Unicode(
        help="The path of the configuration file",
        command_line=True)

    ##########
    # Configuration file options. All of these come from the config file.
    tls = Bool(default_value=False,
               help="If True, connect to docker with --tls",
               config_file=True)

    tls_verify = Bool(default_value=False,
                      help="If True, connect to docker with --tlsverify",
                      config_file=True)

    tls_ca = Unicode(default_value="",
                     help="Path to CA certificate for docker TLS",
                     config_file=True)

    tls_cert = Unicode(default_value="",
                       help="Path to client certificate for docker TLS",
                       config_file=True
                       )

    tls_key = Unicode(default_value="",
                      help="Path to client key for docker TLS",
                      config_file=True)

    docker_host = Unicode(default_value="",
                          help="The docker host to connect to",
                          config_file=True)

    db_url = Unicode(default_value="sqlite:///remoteappmanager.db",
                     help="The url of the database, in sqlalchemy format.",
                     config_file=True)

    login_url = Unicode(default_value="/hub", config_file=True,
                        help=("The url to be redirected to if the user is not "
                              "authenticated for pages that require "
                              "authentication."))

    # The network timeout for any async operation we have to perform,
    # in seconds. 30 seconds is plenty enough.
    network_timeout = Int(default_value=30,
                          help="The timeout (seconds) for network operations",
                          config_file=True)

    template_path = Unicode(
        default_value=paths.template_dir,
        help="The path where to search for jinja templates",
        config_file=True)

    static_path = Unicode(
        default_value=paths.static_dir,
        help="The path where to search for static files",
        config_file=True)

    # Used to keep track if we already added the options
    # to the global config object. If that's the case, we skip the addition
    # to the command line global option object, or we will encounter a
    # redefinition error at define()
    command_line_options_inited = False

    def parse_config(self):
        """Parses the command line arguments and config file, and assign their
        values to our local traits.

        Only the traitlets with the command_line metadata set to True will be
        exported to the command line.
        Traitlets with config_file will instead be retrieved from the
        configuration file.
        """

        # Keep the file line parser isolated, but use the global one
        # so that we can get the help of the command line options.
        file_line_parser = tornado.options.OptionParser()

        for traitlet_name, traitlet in self.traits().items():
            if (traitlet.metadata.get("command_line", False) and not
                    self.command_line_options_inited):
                define(
                    traitlet_name,
                    default=traitlet.default_value,
                    type=type(traitlet.default_value),
                    help=traitlet.help)
            elif traitlet.metadata.get("config_file", False):
                file_line_parser.define(
                    traitlet_name,
                    default=traitlet.default_value,
                    type=type(traitlet.default_value),
                    help=traitlet.help)

        self.__class__.command_line_options_inited = True

        tornado.options.parse_command_line()

        self._transfer_config(options, "command_line")

        # Let it raise the exception if the file is not there.
        # We always want the config file to be present, even if empty
        file_line_parser.parse_config_file(self.config_file)

        self._transfer_config(file_line_parser, "config_file")

        # Normalize the base_url to end with a slash
        self.base_url = with_end_slash(self.base_url)

    def as_dict(self):
        """Returns the configuration class as a dictionary"""
        return {attr: getattr(self, attr) for attr in self.trait_names()}

    def _transfer_config(self, options_object, metadata_identifier):
        """Helper routine. Moves the acquired info from the tornado options
        to this object, trait by trait.
        """
        for traitlet_name, traitlet in self.traits().items():
            if traitlet.metadata.get(metadata_identifier, False):
                self.set_trait(traitlet_name, options_object[traitlet_name])
