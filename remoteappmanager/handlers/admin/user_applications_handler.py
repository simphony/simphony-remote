from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler


class UserApplicationsHandler(BaseHandler):
    """Render the user list"""

    @web.authenticated
    @gen.coroutine
    def get(self, id):
        db = self.application.db
        user = db.get_user(id=id)

        if user is None:
            raise web.HTTPError(404)

        apps = db.get_apps_for_user(user)

        headers = ["Mapping ID",
                   "Application",
                   "Home",
                   "View",
                   "Vol. source",
                   "Vol. target",
                   "Vol. mode"]

        table = [(mapping_id,
                  app.image,
                  policy.allow_home,
                  policy.allow_view,
                  policy.volume_source,
                  policy.volume_target,
                  policy.volume_mode
                  ) for mapping_id, app, policy in apps]

        self.render('admin/tabular.html',
                    table=table,
                    headers=headers,
                    table_title="Applications for User: {}".format(
                        user.name
                    ))
