from http.client import responses
import hashlib

from tornado import web, gen

from jupyterhub.services.auth import HubOAuthenticated

from remoteappmanager.logging.logging_mixin import LoggingMixin
from remoteappmanager.handlers.handler_authenticator import HubOAuthenticator


class BaseHandler(web.RequestHandler, HubOAuthenticated, LoggingMixin):
    """Base class for the request handler."""

    #: The authenticator that is used by tornadowebapi to recognize
    #: the user.
    authenticator = HubOAuthenticator

    @web.authenticated
    @gen.coroutine
    def prepare(self):
        """Runs before any specific handler. """

        # Note that this additional authentication layer is only
        # required to support the tornadowebapi framework - the
        # actual handshake with JupyterHub is handled by the
        # HubOAuthenticated mixin

        # Authenticate the user against the hub.
        self.current_user = yield self.authenticator.authenticate(self)

    def render(self, template_name, **kwargs):
        """Reimplements render to pass well known information to the rendering
        context.
        """
        command_line_config = self.application.command_line_config
        file_config = self.application.file_config

        args = dict(
            user=self.current_user,
            base_url=command_line_config.base_urlpath,
            logout_url=command_line_config.logout_url
        )

        args.update(kwargs)

        args.update({
            "analytics": {
                "tracking_id": file_config.ga_tracking_id
            } if file_config.ga_tracking_id else None
        })

        args.update({
            "gravatar_id": (
                hashlib.md5(
                    str(self.current_user.name).strip().lower().encode(
                        "utf-8")).hexdigest()
                if self.current_user is not None
                else None)
        })

        super(BaseHandler, self).render(template_name, **args)

    def write_error(self, status_code, **kwargs):
        """Render error page for uncaught errors"""

        # if it's a 404, just report it as such
        if status_code == 404:
            self.render('error.html',
                        status_code=status_code,
                        status_message="Not found",
                        message="Not found")
            return

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
