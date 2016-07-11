import requests
from urllib.parse import quote

from traitlets import HasTraits, Unicode

from remoteappmanager.logging.logging_mixin import LoggingMixin
from remoteappmanager.utils import url_path_join


class Hub(LoggingMixin, HasTraits):
    """Provides access to JupyterHub authenticator services."""

    #: The url at which the Hub can be reached
    endpoint_url = Unicode()

    #: The api key to authenticate the request
    api_key = Unicode()

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
            information from jupyterhub associated with the given encryted
            cookie.  Otherwise the dictionary is empty.
        """

        # URL for the authorization requiest
        request_url = url_path_join(self.endpoint_url,
                                    "authorizations/cookie",
                                    cookie_name,
                                    quote(encrypted_cookie, safe=''))

        r = requests.get(request_url,
                         headers={'Authorization': 'token %s' % self.api_key})

        self.log.info(str(r.__dict__))
        if r.status_code < 400:
            return r.json()
        else:
            return {}
