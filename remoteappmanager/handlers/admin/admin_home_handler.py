from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler


class AdminHomeHandler(BaseHandler):
    """Render the admin home page"""

    @web.authenticated
    @gen.coroutine
    def get(self):
        self.render('admin/page.html')
