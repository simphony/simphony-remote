from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler


class AdminHomeHandler(BaseHandler):
    """Render the admin home page"""

    @web.authenticated
    @gen.coroutine
    def get(self):
        app = self.application
        manager = self.application.container_manager
        containers = (yield manager.find_containers())

        context = dict(
            tab="home",
            realm=app.file_config.docker_realm,
            num_total_users=len(app.db.list_users()),
            num_active_users=len(set([c.user for c in containers])),
            num_images=len(app.db.list_applications()),
            num_running_containers=len(containers)
        )
        self.render('admin/home.html', **context)
