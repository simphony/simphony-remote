from tornado import gen

from tornadowebapi.traitlets import Unicode, Int
from tornadowebapi.singleton_resource import SingletonResource
from tornadowebapi.resource_handler import ResourceHandler

from remoteappmanager.webapi.decorators import authenticated


class Stats(SingletonResource):
    #: The current realm of the application
    realm = Unicode(allow_empty=False, strip=True)
    #: Total number of users on the system
    num_total_users = Int()
    #: Total number of users currently running at least one container
    num_active_users = Int()
    #: Total number of available applications.
    num_application = Int()
    #: Total number of running containers.
    num_running_containers = Int()


class StatsHandler(ResourceHandler):
    """Provides statistics about the service."""
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
        resource.num_applications = len(app.db.list_applications())
        resource.num_running_containers = len(containers)
