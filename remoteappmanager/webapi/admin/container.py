from tornado import gen

from tornadowebapi import exceptions
from tornadowebapi.resource import Resource
from tornadowebapi.resource_handler import ResourceHandler
from tornadowebapi.traitlets import Unicode

from remoteappmanager.webapi.decorators import authenticated


class Container(Resource):
    docker_id = Unicode()
    name = Unicode()
    image_name = Unicode()
    image_id = Unicode()
    mapping_id = Unicode()
    user = Unicode()
    realm = Unicode()


class ContainerHandler(ResourceHandler):
    resource_class = Container

    @gen.coroutine
    @authenticated
    def delete(self, resource, **kwargs):
        """Stop the container."""
        identifier = resource.identifier
        container_manager = self.application.container_manager
        container = yield container_manager.find_container(
            url_id=identifier)

        if not container:
            raise exceptions.NotFound()

        try:
            yield self.application.reverse_proxy.unregister(container.urlpath)
        except Exception:
            # If we can't remove the reverse proxy, we cannot do much more
            # than log the problem and keep going, because we want to stop
            # the container regardless.
            self.log.exception(
                "Could not remove reverse proxy for id {}".format(
                    identifier))

        try:
            yield container_manager.stop_and_remove_container(
                container.docker_id)
        except Exception:
            self.log.exception(
                "Could not stop and remove container for id {}".format(
                    identifier))

    @gen.coroutine
    @authenticated
    def items(self, items_response, **kwargs):
        manager = self.application.container_manager
        containers = (yield manager.find_containers())

        items = []
        for c in containers:
            item = Container(identifier=c.url_id)
            item.fill(c)
            items.append(item)

        items_response.set(items)
