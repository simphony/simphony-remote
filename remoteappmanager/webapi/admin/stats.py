from tornado import gen

from tornadowebapi.traitlets import Unicode, Int
from tornadowebapi.singleton_resource import SingletonResource
from tornadowebapi.resource_handler import ResourceHandler

from remoteappmanager.webapi.decorators import authenticated


class Stats(SingletonResource):
    realm = Unicode(allow_empty=False, strip=True)
    num_total_users = Int()
    num_active_users = Int()
    num_images = Int()
    num_running_containers = Int()


class StatsHandler(ResourceHandler):
    resource_class = Stats

    @gen.coroutine
    @authenticated
    def retrieve(self, resource, **kwargs):
        app = self.application
        manager = self.application.container_manager
        containers = (yield manager.find_containers())

        resource.realm = app.file_config.docker_realm
        resource.num_total_users = len(app.db.list_users())
        resource.num_active_users = len(set([c.user for c in containers]))
        resource.num_images = len(app.db.list_applications())
        resource.num_running_containers = len(containers)
