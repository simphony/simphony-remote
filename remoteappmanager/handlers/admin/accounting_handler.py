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

        accountings = db.get_accounting_for_user(acc_user)

        info = [{"mapping_id": accounting.id,
                 "app": accounting.application,
                 "policy": accounting.application_policy}
                for accounting in accountings]

        self.render('admin/accounting.html',
                    info=info,
                    acc_user=acc_user,
                    tab="users")
