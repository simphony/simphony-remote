import requests
from urllib.parse import quote

from tornado.httpclient import HTTPError
from traitlets import HasTraits, Unicode

from remoteappmanager.logging.logging_mixin import LoggingMixin
from remoteappmanager.utils import url_path_join


class Hub(LoggingMixin, HasTraits):
    endpoint_url = Unicode()

    api_key = Unicode()

    def verify_token(self, cookie_name, encrypted_cookie):
        """Return True if cookie is verified as valid.
        Otherwise, raise an HTTPError
        """

        # URL for the authorization requiest
        request_url = url_path_join(self.endpoint_url,
                                    "authorizations/cookie",
                                    cookie_name,
                                    quote(encrypted_cookie, safe=''))

        r = requests.get(request_url,
                         headers={'Authorization': 'token %s' % self.api_key})

        if r.status_code == 403:
            self.log.error("Auth token may have expired: [%i] %s",
                           r.status_code, r.reason)
            raise HTTPError(500,
                            "Permission failure checking authorization, "
                            "please restart.")
        elif r.status_code >= 400:
            self.log.warn("Failed to check authorization: [%i] %s",
                          r.status_code, r.reason)
            raise HTTPError(500, "Failed to check authorization")

        return True
