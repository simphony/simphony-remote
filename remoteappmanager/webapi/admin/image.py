from tornado import gen

from tornadowebapi import exceptions
from tornadowebapi.resource import Resource
from tornadowebapi.resource_handler import ResourceHandler
from tornadowebapi.traitlets import Unicode

from remoteappmanager.webapi.decorators import authenticated
from remoteappmanager.db import exceptions as db_exceptions


class Image(Resource):
    name = Unicode(allow_empty=False, strip=True)


class ImageHandler(ResourceHandler):
    resource_class = Image

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
            db.remove_image(id=id)
            self.log.info("Removed image with id {}".format(id))
        except db_exceptions.NotFound:
            raise exceptions.NotFound()
        except db_exceptions.UnsupportedOperation:
            raise exceptions.Unable()

    @gen.coroutine
    @authenticated
    def create(self, resource, **kwargs):
        db = self.application.db
        try:
            id = db.create_image(resource.name)
        except db_exceptions.Exists:
            raise exceptions.Exists()
        except db_exceptions.UnsupportedOperation:
            raise exceptions.Unable()

        resource.identifier = str(id)

    @gen.coroutine
    @authenticated
    def items(self, items_response, **kwargs):
        """Produces a list of Images items in the items_response object.

        Parameters
        ----------
        items_response: ItemsResponse
            an object to be filled with the appropriate information
        """
        db = self.application.db
        images = db.list_images()

        items = []
        for image in images:
            item = Image(identifier=str(image.id), name=image.name)
            items.append(item)

        items_response.set(items)
