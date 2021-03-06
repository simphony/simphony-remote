from tornado import gen

from tornadowebapi import exceptions
from tornadowebapi.resource import Resource
from tornadowebapi.resource_handler import ResourceHandler
from tornadowebapi.traitlets import Unicode

from remoteappmanager.webapi.decorators import authenticated
from remoteappmanager.db import exceptions as db_exceptions


class User(Resource):
    name = Unicode(allow_empty=False, strip=True)


class UserHandler(ResourceHandler):
    resource_class = User

    @gen.coroutine
    @authenticated
    def delete(self, resource, **kwargs):
        db = self.application.db
        try:
            identifier = int(resource.identifier)
        except ValueError:
            raise exceptions.NotFound()

        try:
            db.remove_user(id=identifier)
            self.log.info("Removed user with id {}".format(identifier))
        except db_exceptions.NotFound:
            raise exceptions.NotFound()
        except db_exceptions.UnsupportedOperation:
            raise exceptions.Unable()

    @gen.coroutine
    @authenticated
    def create(self, resource, **kwargs):
        name = resource.name

        db = self.application.db
        try:
            resource.identifier = str(db.create_user(name))
        except db_exceptions.Exists:
            raise exceptions.Exists()
        except db_exceptions.UnsupportedOperation:
            raise exceptions.Unable()

    @gen.coroutine
    @authenticated
    def items(self, items_response, **kwargs):
        """Produces a list of User items in the items_response object.

        Parameters
        ----------
        items_response: ItemsResponse
            an object to be filled with the appropriate information
        """
        users = self.application.db.list_users()

        items_response.set([
            User(identifier=str(u.id), name=u.name)
            for u in users])
