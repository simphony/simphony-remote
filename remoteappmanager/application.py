from tornado import web
import os

from remoteappmanager.base_application import BaseApplication
from remoteappmanager.handlers.api import RegisterContainerHandler
from remoteappmanager.utils import url_path_join, without_end_slash
from remoteappmanager import webapi


class Application(BaseApplication):
    """Tornado main application"""

    def _webapi_resources(self):
        return [webapi.Application,
                webapi.Container]

    def _web_handlers(self):
        base_urlpath = self.command_line_config.base_urlpath
        return [
            (without_end_slash(
                url_path_join(base_urlpath, "containers", "([a-z0-9_]*)")
            )+"/?", RegisterContainerHandler),
            (
                url_path_join(base_urlpath, '(.*)'),
                web.StaticFileHandler,
                {'path': os.path.join(
                    os.path.dirname(
                        os.path.abspath(__file__),
                    ),
                    'static',
                    'dist'
                ),
                    'default_filename': 'index.html'
                }
            ),
            (base_urlpath.rstrip('/'), web.RedirectHandler, {
                "url": base_urlpath}),
        ]
