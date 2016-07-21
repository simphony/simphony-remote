import os

import tornado.options
from docker import tls
from traitlets import HasTraits, Int, Unicode, Bool, Dict

from remoteappmanager import paths
from remoteappmanager.traitlets import set_traits_from_dict


class FileConfig(HasTraits):
    """Configuration options for the application server.
    They are sourced from the configuration file.
    """

    ##########
    # Configuration file options. All of these come from the config file.

    #: Enable tls, with a twist. if we use self-signed certificates,
    #: using tls as True will produce an error of incorrect CA validation.
    #: As a consequence, defaults to False. TLS secure connection will still
    #: happen thanks to tls_verify and tls[_cert|_key|_ca] being defined.
    #: See https://docs.docker.com/engine/security/https/
    #: Verification can be enabled simply by issuing tls=True in the
    #: config file
    tls = Bool(False,
               help="If True, connect to docker with --tls")

    tls_verify = Bool(False,
                      help="If True, connect to docker with --tlsverify")

    tls_ca = Unicode("", help="Path to CA certificate for docker TLS")

    tls_cert = Unicode("", help="Path to client certificate for docker TLS")

    tls_key = Unicode("", help="Path to client key for docker TLS")

    docker_host = Unicode("", help="The docker host to connect to")

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
        # Sets the default of the docker configuration options from the
        # current environment. These will possibly be overridded by
        # the appropriate entries in the configuration file when parse_file
        # is invoked

        env = os.environ

        self.docker_host = env.get("DOCKER_HOST", "")
        if self.docker_host == "":
            self.docker_host = "unix://var/run/docker.sock"

        self.tls_verify = (env.get("DOCKER_TLS_VERIFY", "") != "")

        # Note that certificate paths can still be present even if tls_verify
        # is false: that is the case of using certificates signed by an
        # authoritative CA.
        cert_path = env.get("DOCKER_CERT_PATH",
                            os.path.join(os.path.expanduser("~"), ".docker"))

        self.tls_cert = os.path.join(cert_path, 'cert.pem')
        self.tls_key = os.path.join(cert_path, 'key.pem')
        self.tls_ca = os.path.join(cert_path, 'ca.pem')

        if self.tls_verify or self.tls:
            self.docker_host = self.docker_host.replace('tcp://', 'https://')

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
            default_value = getattr(self, traitlet_name)

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

        set_traits_from_dict(self, file_line_parser.as_dict())

        if self.tls or self.tls_verify:
            self.docker_host = self.docker_host.replace('tcp://', 'https://')

    def docker_config(self):
        """Extracts the docker configuration as a dictionary suitable
        to be passed as keywords to the docker client.
        """
        params = {}
        params["base_url"] = self.docker_host

        # Note that this will throw if the certificates are not
        # present at the specified paths.
        # Note that the tls flag takes precedence against tls verify.
        # This is docker behavior.
        if self.tls:
            params["tls"] = tls.TLSConfig(
                client_cert=(self.tls_cert, self.tls_key),
                )
        elif self.tls_verify:
            params["tls"] = tls.TLSConfig(
                client_cert=(self.tls_cert, self.tls_key),
                ca_cert=self.tls_ca,
                verify=True,
            )

        params["version"] = "auto"

        return params
