from urllib import parse

from tornado import gen, httpclient
from jupyterhub import orm as jupyterhub_orm
from traitlets import HasTraits, Unicode

from remoteappmanager.logging.logging_mixin import LoggingMixin


class ReverseProxy(LoggingMixin, HasTraits):
    """Represents the remote reverse proxy. It is meant to have a high
    level API."""
    #: The endpoint url at which the reverse proxy has its api
    endpoint_url = Unicode()

    #: The authorization token to authenticate the request
    auth_token = Unicode()

    def __init__(self, *args, **kwargs):
        """Initializes the reverse proxy connection object."""
        super().__init__(*args, **kwargs)

        # Note, we use jupyterhub orm Proxy, but not for database access,
        # just for interface convenience.
        self._reverse_proxy = jupyterhub_orm.Proxy(
            auth_token=self.auth_token,
            api_server=_server_from_url(self.endpoint_url)
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


def _server_from_url(url):
    """Creates a orm.Server from a given url"""
    parsed = parse.urlparse(url)
    return jupyterhub_orm.Server(
        proto=parsed.scheme,
        ip=parsed.hostname,
        port=parsed.port,
        base_url=parsed.path
    )
