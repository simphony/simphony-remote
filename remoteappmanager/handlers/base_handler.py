from urllib.parse import urljoin

from tornado import web, gen

from remoteappmanager.logging.logging_mixin import LoggingMixin


class BaseHandler(web.RequestHandler, LoggingMixin):
    """Base class for the request handler."""

    @gen.coroutine
    def prepare(self):
        """Runs before any specific handler. """

        # Authenticate the user against the hub. We can't use get_current_user
        # because we want to do it asynchronously.
        hub = self.application.hub
        cookie_name = self.settings["cookie_name"]
        user_cookie = self.get_cookie(cookie_name)
        user = None

        if user_cookie:
            user_data = (yield hub.verify_token(cookie_name, user_cookie))
            if user_data.get('name', '') == self.application.user.name:
                user = self.application.user

        self.current_user = user

    def render(self, template_name, **kwargs):
        """Reimplements render to pass well known information to the rendering
        context.
        """
        args = dict(
            user=self.current_user,
            base_url=self.application.command_line_config.base_url,
            logout_url=urljoin(
                self.application.command_line_config.hub_prefix,
                "logout")
        )

        args.update(kwargs)
        super(BaseHandler, self).render(template_name, **args)
