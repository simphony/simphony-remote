import uuid
import types

from traitlets import (
    HasTraits,
    Instance,
    default
)


def issue(self, message, exc=None):
    """Accepts a message that will be logged with an additional reference
    code for easy log lookup.

    The identifier will be returned for inclusion in user-visible
    error messages.
    """
    ref = str(uuid.uuid1())

    if exc is None:
        err_message = "{}. Ref: {}".format(message, ref)
    else:
        err_message = "{} : {}. Ref: {}".format(
            message, str(exc), ref)

    self.error(err_message)
    return ref


class LoggingMixin(HasTraits):
    """A HasTrait class that provides logging. Used as a mixin.
    """

    log = Instance('logging.Logger')

    @default('log')
    def _log_default(self):
        from tornado.log import app_log

        # monkey patch the logger to provide an additional method that handles
        # issues
        app_log.issue = types.MethodType(issue, app_log)
        return app_log
