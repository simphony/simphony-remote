from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler


class UserHomeHandler(BaseHandler):
    """Render the user's home page"""

    @web.authenticated
    @gen.coroutine
    def get(self):
        self.render('user/page.html')
