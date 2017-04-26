from tornado import gen
from tornadowebapi.resource_handler import ResourceHandler
from tornadowebapi.traitlets import Absent, Unicode, Bool

from remoteappmanager.utils import parse_volume_string
from tornadowebapi import exceptions
from tornadowebapi.resource import Resource

from remoteappmanager.webapi.decorators import authenticated
from remoteappmanager.db import exceptions as db_exceptions


class Accounting(Resource):
    user_name = Unicode(allow_empty=False, strip=True)
    image_name = Unicode(allow_empty=False, strip=True)
    allow_home = Bool()
    volume = Unicode(optional=True, allow_empty=False, strip=True)

    @classmethod
    def collection_name(cls):
        return "accounting"


class AccountingHandler(ResourceHandler):
    resource_class = Accounting

    @gen.coroutine
    @authenticated
    def create(self, resource, **kwargs):
        db = self.application.db

        volume = {} if resource.volume == Absent else resource.volume
        parse_volume_string(volume)

        try:
            id = db.grant_access(
                resource.image_name,
                resource.user_name,
                resource.allow_home,
                True,
                volume,
                )
        except db_exceptions.NotFound:
            raise exceptions.NotFound()

        resource.identifier = id

    @gen.coroutine
    @authenticated
    def delete(self, resource, **kwargs):
        db = self.application.db

        try:
            db.revoke_access_by_id(resource.identifier)
        except db_exceptions.NotFound:
            raise exceptions.NotFound()


def _not_empty_str(value):
    value = str(value).strip()

    if len(value) == 0:
        raise ValueError("Value cannot be empty")

    return value
