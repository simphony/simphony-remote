from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler


class ContainersHandler(BaseHandler):
    """Render the admin containers list"""

    @web.authenticated
    @gen.coroutine
    def get(self):
        manager = self.application.container_manager
        containers = (yield manager.running_containers())

        headers = ["user", "image", "docker id", "mapping id"]

        table = [
            (c.user, c.image_name, c.docker_id, c.mapping_id)
            for c in containers
        ]

        self.render('admin/tabular.html',
                    headers=headers,
                    table=table,
                    controller="containers")
