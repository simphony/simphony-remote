from remoteappmanager.traitlets import UnicodeOrFalse
from traitlets import HasTraits, Bool, Unicode


class DockerClientConfig(HasTraits):
    use_docker_client_env = Bool(False,
                                 config=True,
                                 help="If True, will use Docker client env "
                                      "variable (boot2docker friendly)")

    tls = Bool(False,
               help="If True, connect to docker with --tls")

    tls_verify = Bool(False,
                      help="If True, connect to docker with --tlsverify")

    tls_ca = Unicode("",
                     help="Path to CA certificate for docker TLS")

    tls_cert = Unicode("",
                       help="Path to client certificate for docker TLS")

    tls_key = Unicode("",
                      help="Path to client key for docker TLS")

    tls_assert_hostname = UnicodeOrFalse(default_value=None,
                                         allow_none=True,
                                         help="If False, do not verify "
                                              "hostname of docker daemon",
                                         )
    docker_host = Unicode("",
                          help="Docker host to which to connect to.")

    @property
    def tls_client(self):
        """A tuple consisting of the TLS client certificate and key if they
        have been provided, otherwise None.
        """
        if self.tls_cert and self.tls_key:
            return (self.tls_cert, self.tls_key)

        return None
