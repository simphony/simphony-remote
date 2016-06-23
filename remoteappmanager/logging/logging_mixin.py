from traitlets import (
    HasTraits,
    Instance,
    default
)


class LoggingMixin(HasTraits):
    """A HasTrait class that provides logging. Used as a mixin.
    """

    log = Instance('logging.Logger')

    @default('log')
    def _log_default(self):
        from traitlets import log
        return log.get_logger()
