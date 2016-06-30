import requests
from urllib.parse import urljoin, quote

from tornado import web
from tornado.httpclient import HTTPError
from notebook.utils import url_path_join

from remoteappmanager.logging.logging_mixin import LoggingMixin


class BaseHandler(web.RequestHandler, LoggingMixin):
    """Base class for the request handler."""

    def get_current_user(self):
        user_cookie = self.get_cookie(self.settings['cookie_name'])
        if user_cookie:
            verified = self.verify_token(self.settings['cookie_name'],
                                         user_cookie)
            if verified:
                return self.application.user

        return None

    def render(self, template_name, **kwargs):
        """Reimplements render to pass well known information to the rendering
        context.
        """
        args = dict(
            user=self.current_user,
            base_url=self.application.config.base_url,
            logout_url=urljoin(self.application.config.hub_prefix, "logout"))

        args.update(kwargs)
        super(BaseHandler, self).render(template_name, **args)

    def verify_token(self, cookie_name, encrypted_cookie):
        """Return True if cookie is verified as valid.
        Otherwise, raise an HTTPError
        """
        hub_api_url = self.settings['hub_api_url']
        hub_api_key = self.settings['hub_api_key']

        r = requests.get(url_path_join(hub_api_url,
                                       "authorizations/cookie",
                                       cookie_name,
                                       quote(encrypted_cookie, safe='')),
                         headers={'Authorization': 'token %s' % hub_api_key})

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
