from urllib.parse import quote, urlparse

from tornado import gen, escape
from tornado.httpclient import AsyncHTTPClient
from traitlets import HasTraits, Unicode

from jupyterhub.services.auth import (
    HubOAuth, HubOAuthCallbackHandler)

from remoteappmanager.logging.logging_mixin import LoggingMixin
from remoteappmanager.utils import url_path_join


class Hub(LoggingMixin, HasTraits):
    """Provides access to JupyterHub authenticator services."""

    #: The url at which the JupyterHub can be reached
    endpoint_url = Unicode()

    #: The api token to authenticate the request
    api_token = Unicode()

    #: The base urlpath for the current user.
    base_url = Unicode()

    #: The url prefix of the JupyterHub
    hub_prefix = Unicode()

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

        # Create connection to JupyterHub's OAuth services
        self._hub_auth = HubOAuth(
            hub_api_url=self.endpoint_url,
            api_token=self.api_token,
            base_url=self.base_url,
            hub_prefix=self.hub_prefix,
        )

    @gen.coroutine
    def verify_token(self, cookie_name, encrypted_cookie):
        """Verify the authentication token and grants access to the user
        if verified.

        Deprecated as of remoteappmanager 2.2.0

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

    @gen.coroutine
    def get_user(self, handler):
        """Verify the authentication details present in the handler
        session

        Parameters
        ----------
        handler : tornado.web.RequestHandler
            Request handler to be inspected. Expected to have inherited
            from the JupyterHub HubOAuthenticated mixin

        Returns
        -------
        user_data : dict
            If authentication is successful, user_data contains the user's
            information from jupyterhub associated with the given encrypted
            cookie.  Otherwise the dictionary is empty.
        """
        return self._hub_auth.get_user(handler)

    def callback_handlers(self):
        """Add callback url to enable OAuth with JupyterHub
        """
        return [(
            urlparse(self._hub_auth.oauth_redirect_uri).path,
            HubOAuthCallbackHandler
        )]
