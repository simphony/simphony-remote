from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler
from remoteappmanager.webutils import Link


class UsersHandler(BaseHandler):
    """Render the user list"""

    @web.authenticated
    @gen.coroutine
    def get(self):
        db = self.application.db
        users = db.list_users()

        headers = ["ID", "User", "Applications"]

        table = [
            (user.id, user.name, Link(text="Show",
                                      rel_urlpath="users/{}/".format(user.id)))
            for user in users
            ]

        self.render('admin/tabular.html',
                    headers=headers,
                    table=table,
                    table_title="Users")
