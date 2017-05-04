from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler


class UsersHandler(BaseHandler):
    """Render the user list"""

    @web.authenticated
    @gen.coroutine
    def get(self):
        db = self.application.db
        users = db.list_users()

        self.render('admin/users.html',
                    users=users,
                    tab="users")