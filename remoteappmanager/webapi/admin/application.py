from tornado import gen

from tornadowebapi import exceptions
from tornadowebapi.resource import Resource
from tornadowebapi.resource_handler import ResourceHandler
from tornadowebapi.traitlets import Unicode, Bool

from remoteappmanager.webapi.decorators import authenticated
from remoteappmanager.db import exceptions as db_exceptions


class Application(Resource):
    image_name = Unicode(allow_empty=False, strip=True)
    db_image = Bool(True)


class ApplicationHandler(ResourceHandler):
    resource_class = Application

    @gen.coroutine
    @authenticated
    def delete(self, resource, **kwargs):
        """Removes the application."""
        db = self.application.db
        try:
            id = int(resource.identifier)
        except ValueError:
            raise exceptions.NotFound()

        try:
            db.remove_application(id=id)
            self.log.info("Removed application with id {}".format(id))
        except db_exceptions.NotFound:
            raise exceptions.NotFound()
        except db_exceptions.UnsupportedOperation:
            raise exceptions.Unable()

    @gen.coroutine
    @authenticated
    def create(self, resource, **kwargs):
        db = self.application.db
        try:
            id = db.create_application(resource.image_name)
        except db_exceptions.Exists:
            raise exceptions.Exists()
        except db_exceptions.UnsupportedOperation:
            raise exceptions.Unable()

        resource.identifier = str(id)

    @gen.coroutine
    @authenticated
    def items(self, items_response, **kwargs):
        """Produces a list of Application items in the items_response object.

        Parameters
        ----------
        items_response: ItemsResponse
            an object to be filled with the appropriate information
        """
        docker_images = yield self.application.container_manager.images()
        docker_images = [
            image for image in docker_images
            if image.type in ["webapp", "vncapp"]
        ]

        db = self.application.db
        apps = db.list_applications()
        app_names = [app.image for app in apps]

        items = []
        for app in apps:
            item = Application(identifier=str(app.id), image_name=app.image)
            items.append(item)

        for image in docker_images:
            image_name = image.name.split(":")[0]
            if image_name not in app_names:
                item = Application(
                    identifier=image.docker_id,
                    image_name=image_name,
                    db_image=False
                )
                items.append(item)

        items_response.set(items)
