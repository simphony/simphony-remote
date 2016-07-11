from urllib.parse import quote

from tornado.httpclient import HTTPError, AsyncHTTPClient
from tornado import gen
from traitlets import HasTraits, Unicode

from remoteappmanager.logging.logging_mixin import LoggingMixin
from remoteappmanager.utils import url_path_join


class Hub(LoggingMixin, HasTraits):
    """Provides access to JupyterHub authenticator services."""

    #: The url at which the Hub can be reached
    endpoint_url = Unicode()

    #: The api key to authenticate the request
    api_key = Unicode()

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
        True if cookie is verified as valid. Otherwise, raise an HTTPError
        """

        # URL for the authorization requiest
        request_url = url_path_join(self.endpoint_url,
                                    "authorizations/cookie",
                                    cookie_name,
                                    quote(encrypted_cookie, safe=''))

        client = AsyncHTTPClient()
        r = yield client.fetch(
            request_url,
            headers={'Authorization': 'token %s' % self.api_key})

        if r.code == 403:
            self.log.error("Auth token may have expired: [%i] %s",
                           r.code, r.reason)
            raise HTTPError(500,
                            "Permission failure checking authorization, "
                            "please restart.")
        elif r.code >= 400:
            self.log.warn("Failed to check authorization: [%i] %s",
                          r.code, r.reason)
            raise HTTPError(500, "Failed to check authorization")

        return True
