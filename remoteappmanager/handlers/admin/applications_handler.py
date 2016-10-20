from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler


class ApplicationsHandler(BaseHandler):
    """Render the application list"""

    @web.authenticated
    @gen.coroutine
    def get(self):
        db = self.application.db
        apps = db.list_applications()
        headers = ["ID", "Image"]

        table = [(app.id, app.image) for app in apps]

        self.render('admin/tabular.html',
                    table=table,
                    headers=headers,
                    table_title="Registered Applications",
                    tab="applications")
