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
            db.remove_user(id=int(resource.identifier))
            self.log.info("Removed user with id {}".format(
                resource.identifier))
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
