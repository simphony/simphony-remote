from tornado import web

from remoteappmanager.base_application import BaseApplication
from remoteappmanager.handlers.api import (
    AdminHomeHandler,
)
from remoteappmanager.webapi import admin


class AdminApplication(BaseApplication):
    """Tornado main application"""

    def _webapi_resources(self):
        return [admin.ContainerHandler,
                admin.ImageHandler,
                admin.UserHandler,
                admin.AccountingHandler,
                admin.StatsHandler]

    def _web_handlers(self):
        base_urlpath = self.command_line_config.base_urlpath
        return [
            (base_urlpath, AdminHomeHandler),
            (base_urlpath.rstrip('/'),
             web.RedirectHandler, {"url": base_urlpath}),
        ]
