from tornado import web

from remoteappmanager.base_application import BaseApplication
from remoteappmanager.handlers.api import HomeHandler
from remoteappmanager import webapi


class Application(BaseApplication):
    """Tornado main application"""

    def _webapi_resources(self):
        return [webapi.Application,
                webapi.Container]

    def _web_handlers(self):
        base_urlpath = self.command_line_config.base_urlpath
        return [
            (base_urlpath, HomeHandler),
            (base_urlpath.rstrip('/'),
             web.RedirectHandler, {"url": base_urlpath}),
        ]
