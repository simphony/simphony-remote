from tornado import gen
from tornadowebapi.exceptions import NotFound, BadQueryArguments, \
    BadRepresentation
from tornadowebapi.resource_handler import ResourceHandler
from tornadowebapi.traitlets import Unicode, Bool

from tornadowebapi import exceptions
from tornadowebapi.resource import Resource
from tornadowebapi.filtering import And, Eq

from remoteappmanager.webapi.decorators import authenticated
from remoteappmanager.db import exceptions as db_exceptions


class Accounting(Resource):
    user_id = Unicode(allow_empty=False, strip=True)
    image_name = Unicode(allow_empty=False, strip=True)
    allow_home = Bool()
    volume_source = Unicode(allow_none=True)
    volume_target = Unicode(allow_none=True)
    volume_mode = Unicode(allow_none=True)

    @classmethod
    def collection_name(cls):
        return "accounting"


class AccountingHandler(ResourceHandler):
    resource_class = Accounting

    @gen.coroutine
    @authenticated
    def create(self, resource, **kwargs):
        db = self.application.db

        acc_user = db.get_user(id=int(resource.user_id))
        if acc_user is None:
            raise BadRepresentation()

        volume = (resource.volume_source +
                  ":"+resource.volume_target +
                  ":"+resource.volume_mode)
        if resource.volume_target == "" or resource.volume_source == "":
            volume = None

        try:
            id = db.grant_access(
                resource.image_name,
                acc_user.name,
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

    @gen.coroutine
    @authenticated
    def items(self, item_response, filter_=None, **kwargs):
        if filter_ is None:
            raise BadQueryArguments("Filter is required")

        db = self.application.db
        if (isinstance(filter_, And) and
                len(filter_.filters) == 1 and
                isinstance(filter_.filters[0], Eq) and
                filter_.filters[0].key == "user_id"):

            user_id = int(filter_.filters[0].value)
            acc_user = db.get_user(id=user_id)
            if acc_user is None:
                raise NotFound()

            accountings = db.get_accounting_for_user(acc_user)

            response = []
            for acc in accountings:
                entry = Accounting(
                    identifier=str(acc.id),
                    user_id=str(acc_user.id),
                    image_name=acc.image.name,
                    allow_home=acc.application_policy.allow_home,
                    volume_source=acc.application_policy.volume_source,
                    volume_target=acc.application_policy.volume_target,
                    volume_mode=acc.application_policy.volume_mode
                )
                response.append(entry)
            item_response.set(response)
        else:
            raise BadQueryArguments("Empty filter specified")
