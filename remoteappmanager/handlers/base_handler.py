from http.client import responses
from urllib.parse import urljoin

from tornado import web, gen

from remoteappmanager.logging.logging_mixin import LoggingMixin
from remoteappmanager.handlers.handler_authenticator import HubAuthenticator


class BaseHandler(web.RequestHandler, LoggingMixin):
    """Base class for the request handler."""

    #: The authenticator that is used to recognize the user.
    authenticator_class = HubAuthenticator

    @gen.coroutine
    def prepare(self):
        """Runs before any specific handler. """

        # Authenticate the user against the hub. We can't use get_current_user
        # because we want to do it asynchronously.
        authenticator = self.authenticator_class()
        self.current_user = yield authenticator.authenticate(self)

    def render(self, template_name, **kwargs):
        """Reimplements render to pass well known information to the rendering
        context.
        """
        args = dict(
            user=self.current_user,
            base_url=self.application.command_line_config.base_urlpath,
            logout_url=urljoin(
                self.application.command_line_config.hub_prefix,
                "logout")
        )

        args.update(kwargs)
        super(BaseHandler, self).render(template_name, **args)

    def write_error(self, status_code, **kwargs):
        """Render error page for uncaught errors"""
        status_message = responses.get(status_code, 'Unknown HTTP Error')
        message = ""

        # If this error was caused by an uncaught exception
        # log exception message and reference number as well
        exc_info = kwargs.get('exc_info')
        if exc_info:
            exception = exc_info[1]
            ref = self.log.issue(status_message, exception)
            reason = getattr(exception, 'reason', '')
            message = '{} Ref.: {}'.format(reason, ref)

        self.render('error.html', status_code=status_code,
                    status_message=status_message, message=message)
