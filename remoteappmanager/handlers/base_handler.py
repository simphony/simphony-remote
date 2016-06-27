from tornado import web
from urllib.parse import urljoin

from remoteappmanager.logging.logging_mixin import LoggingMixin


class BaseHandler(web.RequestHandler, LoggingMixin):
    """Base class for the request handler."""

    def get_current_user(self):
        return self.application.user.name

    def render(self, template_name, **kwargs):
        """Reimplements render to pass well known information to the rendering
        context.
        """
        args = dict(
            user=self.current_user,
            base_url=self.application.config.base_url,
            logout_url=urljoin(self.application.config.hub_prefix, "logout")
        )

        args.update(kwargs)
        super(BaseHandler, self).render(template_name, **args)
