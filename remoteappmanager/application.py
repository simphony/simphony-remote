from tornado import web

from remoteappmanager.base_application import BaseApplication
from remoteappmanager.handlers.api import (
    HomeHandler, ReregisterContainersHandler)
from remoteappmanager.utils import url_path_join, with_end_slash
from remoteappmanager import webapi


class Application(BaseApplication):
    """Tornado main application"""

    def _webapi_resources(self):
        return [webapi.Application,
                webapi.Container]

    def _web_handlers(self):
        base_urlpath = self.command_line_config.base_urlpath
        return [
            (with_end_slash(
                url_path_join(base_urlpath, "containers", "(.*)")
            ), ReregisterContainersHandler),
            (base_urlpath, HomeHandler),
            (base_urlpath.rstrip('/'), web.RedirectHandler, {
                "url": base_urlpath}),
        ]
