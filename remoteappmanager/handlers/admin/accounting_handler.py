from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler


class AccountingHandler(BaseHandler):
    """Render the execution policies for a given user"""
    @web.authenticated
    @gen.coroutine
    def get(self, id):
        id = int(id)

        db = self.application.db
        acc_user = db.get_user(id=id)

        if acc_user is None:
            raise web.HTTPError(404)

        apps = db.get_apps_for_user(acc_user)

        info = [{"mapping_id": mapping_id,
                 "app": app,
                 "policy": policy}
                for mapping_id, app, policy in apps]

        self.render('admin/accounting.html',
                    info=info,
                    acc_user=acc_user,
                    tab="users")
