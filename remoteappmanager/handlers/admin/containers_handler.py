from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler


class ContainersHandler(BaseHandler):
    """Render the admin containers list"""

    @web.authenticated
    @gen.coroutine
    def get(self):
        manager = self.application.container_manager
        containers = (yield manager.find_containers())

        self.render('admin/containers.html',
                    containers=containers,
                    tab="containers")
