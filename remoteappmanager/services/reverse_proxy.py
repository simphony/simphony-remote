from tornado import gen, httpclient
from jupyterhub.proxy import Proxy, ConfigurableHTTPProxy
from traitlets import HasTraits, Unicode, Instance

from remoteappmanager.logging.logging_mixin import LoggingMixin


class ReverseProxy(LoggingMixin, HasTraits):
    """Represents the remote reverse proxy. It is meant to have a high
    level API."""
    #: The endpoint url at which the reverse proxy has its api
    endpoint_url = Unicode()

    #: The authorization API token to authenticate the request
    api_token = Unicode()

    #: Internal instance of the reverse proxy API
    _reverse_proxy = Instance(Proxy)

    def __init__(self, *args, **kwargs):
        """Initializes the reverse proxy connection object."""
        super().__init__(*args, **kwargs)

        if not self.api_token:
            message = ("invalid proxy API Token to initialise "
                       "the reverse proxy connection.")
            self.log.error(message)
            raise ValueError(message)

        if not self.endpoint_url:
            message = ("invalid proxy endpoint url to initialise "
                       "the reverse proxy connection.")
            self.log.error(message)
            raise ValueError(message)

        # Note: we just use the jupyterhub ConfigurableHTTPProxy for
        # interface convenience
        self._reverse_proxy = ConfigurableHTTPProxy(
            auth_token=self.api_token,
            api_url=self.endpoint_url
        )

        self.log.info("Reverse proxy setup on {}".format(
            self.endpoint_url,
        ))

    @gen.coroutine
    def register(self, urlpath, target_host_url):
        """Register a given urlpath to redirect to a different target host.
        The operation is idempotent.

        Parameters
        ----------
        urlpath: str
            The absolute path of the url (e.g. /my/internal/service/)"

        target_host_url:
            The host to redirect to, e.g. http://127.0.0.1:31233/service/
        """
        self.log.info("Registering {} redirection to {}".format(
            urlpath,
            target_host_url))

        yield self._reverse_proxy.api_request(
            urlpath,
            method='POST',
            body=dict(
                target=target_host_url,
            )
        )

    @gen.coroutine
    def unregister(self, urlpath):
        """Unregisters a previously registered urlpath.
        If the urlpath is not found in the reverse proxy, it will not raise
        an error, but it will log the unexpected circumstance.

        Parameters
        ----------
        urlpath: str
            The absolute path of the url (e.g. /my/internal/service/"
        """
        self.log.info("Deregistering {} redirection".format(urlpath))

        try:
            yield self._reverse_proxy.api_request(urlpath, method='DELETE')
        except httpclient.HTTPError as e:
            if e.code == 404:
                self.log.warning("Could not find urlpath {} when removing"
                                 " container. In any case, the reverse proxy"
                                 " does not map the url. Continuing".format(
                                     urlpath))
            else:
                raise e
