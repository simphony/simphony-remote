from tornado import gen

from tornadowebapi import exceptions
from tornadowebapi.resource import Resource

from remoteappmanager.restresources.decorators import authenticated
from remoteappmanager.db import exceptions as db_exceptions


class Application(Resource):
    @gen.coroutine
    @authenticated
    def delete(self, identifier):
        """Stop the container."""
        db = self.application.db
        try:
            id = int(identifier)
        except ValueError:
            raise exceptions.BadRequest("id")

        try:
            db.remove_application(id=id)
            self.log.info("Removed application with id {}".format(id))
        except db_exceptions.NotFound:
            self.log.exception("Could not remove application with "
                               "id {}".format(id))
        except db_exceptions.UnsupportedOperation:
            raise exceptions.Unable()

    @gen.coroutine
    @authenticated
    def create(self, representation):
        try:
            image_name = str(representation["image_name"])
        except KeyError:
            raise exceptions.BadRequest("image_name")

        db = self.application.db
        try:
            id = db.create_application(image_name)
        except (db_exceptions.UnsupportedOperation,
                db_exceptions.Exists):
            raise exceptions.Unable()

        return str(id)
