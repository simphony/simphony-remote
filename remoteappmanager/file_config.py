import tornado.options
import docker.utils
from docker import tls
from traitlets import HasTraits, Int, Unicode, Bool, Dict
from traitlets.utils.sentinel import Sentinel

from remoteappmanager import paths
from remoteappmanager.traitlets import set_traits_from_dict


class FileConfig(HasTraits):
    """Configuration options for the application server.
    They are sourced from the configuration file.
    """

    ##########
    # Configuration file options. All of these come from the config file.
    tls = Bool(help="If True, connect to docker with --tls")

    tls_verify = Bool(help="If True, connect to docker with --tlsverify")

    tls_ca = Unicode(help="Path to CA certificate for docker TLS")

    tls_cert = Unicode(help="Path to client certificate for docker TLS")

    tls_key = Unicode(help="Path to client key for docker TLS")

    docker_host = Unicode(help="The docker host to connect to")

    accounting_class = Unicode(
        default_value="remoteappmanager.db.orm.AppAccounting",
        help="The import path to a subclass of ABCAccounting.")

    accounting_kwargs = Dict(
        default_value={'url': 'sqlite:///remoteappmanager.db'},
        help="The keyword arguments for initialising the Accounting instance")

    login_url = Unicode(default_value="/hub",
                        help=("The url to be redirected to if the user is not "
                              "authenticated for pages that require "
                              "authentication."))

    # The network timeout for any async operation we have to perform,
    # in seconds. 30 seconds is plenty enough.
    network_timeout = Int(default_value=30,
                          help="The timeout (seconds) for network operations")

    template_path = Unicode(
        default_value=paths.template_dir,
        help="The path where to search for jinja templates")

    static_path = Unicode(
        default_value=paths.static_dir,
        help="The path where to search for static files")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        config = docker.utils.kwargs_from_env()
        tls_config = config.get("tls")

        # if we use self-signed certificates, using tls as True
        # will produce an error of incorrect CA validation.
        # As a consequence, we set tls to False by default honoring
        # docker documentation (although not very clear on this point)
        # See https://docs.docker.com/engine/security/https/
        # Verification can be enabled simply by issuing tls=True in the
        # config file
        self.tls = False

        if tls_config is not None:
            self.tls_verify = tls_config.verify
            self.tls_ca = tls_config.ca_cert
            self.tls_cert = tls_config.client_cert[0]
            self.tls_key = tls_config.client_cert[1]

        self.docker_host = config.get("base_url", 'unix://var/run/docker.sock')

    # -------------------------------------------------------------------------
    # Public

    def parse_config(self, config_file):
        """Parses the config file, and assign their values to our local traits.
        """

        if config_file.strip() == '':
            raise tornado.options.Error("Config file must be specified "
                                        "in command line arguments.")

        # Keep the file line parser isolated, but use the global one
        # so that we can get the help of the command line options.
        file_line_parser = tornado.options.OptionParser()

        for traitlet_name, traitlet in self.traits().items():
            # tornado.OptionParser defines an option with a Python type
            # and performs type validation.
            # traitlet.default_value may be a Sentinel value (e.g. Tuple,
            # Dict, Instance), in which case we use the repr
            default_value = traitlet.default_value

            if type(default_value) is Sentinel:
                default_value = eval(traitlet.default_value_repr())

            file_line_parser.define(
                traitlet_name,
                default=default_value,
                type=type(default_value),
                help=traitlet.help)

        # Let it raise the exception if the file is not there.
        # We always want the config file to be present, even if empty
        try:
            file_line_parser.parse_config_file(config_file)
        except FileNotFoundError:
            raise tornado.options.Error(
                'Could not find specified configuration'
                ' file "{}"'.format(config_file))

        set_traits_from_dict(self, file_line_parser)

    def docker_config(self):
        """Extracts the docker configuration as a dictionary suitable
        to be passed as keywords to the docker client"""
        params = dict(
            base_url=self.docker_host,
            tls=tls.TLSConfig(
                client_cert=(self.tls_cert, self.tls_key),
                ca_cert=self.tls_ca,
                verify=self.tls_verify,
                ssl_version="auto",
                assert_hostname=True,
            )
        )

        return params
