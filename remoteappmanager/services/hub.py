from urllib.parse import quote

from tornado import gen, escape
from tornado.httpclient import AsyncHTTPClient
from traitlets import HasTraits, Unicode

from remoteappmanager.logging.logging_mixin import LoggingMixin
from remoteappmanager.utils import url_path_join


class Hub(LoggingMixin, HasTraits):
    """Provides access to JupyterHub authenticator services."""

    #: The url at which the Hub can be reached
    endpoint_url = Unicode()

    #: The api token to authenticate the request
    api_token = Unicode()

    def __init__(self, *args, **kwargs):
        """Initializes the hub connection object."""
        super().__init__(*args, **kwargs)

        if not self.api_token:
            message = ("Invalid API Token to initialise "
                       "the hub connection.")
            self.log.error(message)
            raise ValueError(message)

        if not self.endpoint_url:
            message = ("Invalid endpoint url to initialise "
                       "the hub connection.")
            self.log.error(message)
            raise ValueError(message)

    @gen.coroutine
    def verify_token(self, cookie_name, encrypted_cookie):
        """Verify the authentication token and grants access to the user
        if verified.

        Parameters
        ----------
        cookie_name: str
            A string containing the conventional name of the cookie.
        encrypted_cookie: str
            the cookie content, as received by JupyterHub (encrypted)

        Returns
        -------
        user_data : dict
            If authentication is successful, user_data contains the user's
            information from jupyterhub associated with the given encrypted
            cookie.  Otherwise the dictionary is empty.
        """

        # URL for the authorization request
        request_url = url_path_join(self.endpoint_url,
                                    "authorizations/cookie",
                                    cookie_name,
                                    quote(encrypted_cookie, safe=''))

        client = AsyncHTTPClient()
        r = yield client.fetch(
                request_url,
                headers={'Authorization': 'token %s' % self.api_token},
                raise_error=False)

        if r.code < 400:
            return escape.json_decode(r.body)
        else:
            return {}
