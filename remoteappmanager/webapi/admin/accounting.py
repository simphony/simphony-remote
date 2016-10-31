from tornado import gen

from remoteappmanager.utils import parse_volume_string
from tornadowebapi import exceptions
from tornadowebapi.resource import Resource

from remoteappmanager.webapi.decorators import authenticated
from remoteappmanager.db import exceptions as db_exceptions


class Accounting(Resource):
    __collection_name__ = "accounting"

    def validate(self, representation):
        representation["user_name"] = _not_empty_str(
            representation["user_name"])
        representation["image_name"] = _not_empty_str(
            representation["image_name"])
        representation["allow_home"] = bool(
            representation["allow_home"])

        if "volume" in representation:
            representation["volume"] = _not_empty_str(
                representation["volume"])
            parse_volume_string(representation["volume"])

    @gen.coroutine
    @authenticated
    def create(self, representation):
        db = self.application.db

        try:
            id = db.grant_access(
                representation["image_name"],
                representation["user_name"],
                representation["allow_home"],
                True,
                representation.get("volume")
                )
        except db_exceptions.NotFound:
            raise exceptions.NotFound()

        return id

    @gen.coroutine
    @authenticated
    def delete(self, id):
        db = self.application.db

        try:
            db.revoke_access_by_id(id)
        except db_exceptions.NotFound:
            raise exceptions.NotFound()


def _not_empty_str(value):
    value = str(value).strip()

    if len(value) == 0:
        raise ValueError("Value cannot be empty")

    return value
