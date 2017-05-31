from tornado import gen

from remoteappmanager.webapi.decorators import authenticated
from tornado_rest_jsonapi import (
    Schema,
    ResourceDetails,
    ResourceList,
    ModelConnector,
    fields,
    exceptions
)
from marshmallow import Schema as NestedSchema


class ContainerSchema(NestedSchema):
    name = fields.String(required=True, dump_only=True)
    image_name = fields.String(required=True, dump_only=True)
    url_id = fields.String(required=True, dump_only=True)


class PolicySchema(NestedSchema):
    allow_home = fields.Boolean(required=True, dump_only=True)
    volume_source = fields.String(required=True,
                                  allow_none=True,
                                  dump_only=True)
    volume_target = fields.String(required=True,
                                  allow_none=True,
                                  dump_only=True)
    volume_mode = fields.String(required=True,
                                allow_none=True,
                                dump_only=True)


class ImageSchema(NestedSchema):
    name = fields.String(required=True, dump_only=True)
    ui_name = fields.String(required=True, dump_only=True)
    icon_128 = fields.String(required=True, dump_only=True)
    description = fields.String(required=True, dump_only=True)
    configurables = fields.Method(serialize="serialize_configurables",
                                  required=True, dump_only=True)

    def serialize_configurables(self, obj):
        return [conf.tag for conf in obj.configurables]


class ApplicationSchema(Schema):
    class Meta:
        type_ = "application"

    id = fields.String(required=True)
    image = fields.Nested(ImageSchema, required=True, dump_only=True)
    policy = fields.Nested(PolicySchema, required=True, dump_only=True)
    container = fields.Nested(ContainerSchema, dump_only=True)


class ApplicationConnector(ModelConnector):
    @gen.coroutine
    @authenticated
    def retrieve_object(self, identifier, **kwargs):
        accs = self.application.db.get_accounting_for_user(
            self.current_user.account
        )

        # Convert the list of tuples in a dict
        accs_dict = {
            acc.id: (acc.application, acc.application_policy)
            for acc in accs}

        if identifier not in accs_dict:
            raise exceptions.ObjectNotFound()

        app, policy = accs_dict[identifier]

        container_manager = self.application.container_manager
        image = yield container_manager.image(app.image)
        if image is None:
            # The user has access to an application that is no longer
            # available in docker.
            raise exceptions.ObjectNotFound()

        containers = yield container_manager.find_containers(
            user_name=self.current_user.name,
            mapping_id=identifier)

        app = dict(
            id=identifier,
            image=image,
            policy=policy
        )

        if len(containers):
            # We assume that we can only run one container only (although the
            # API considers a broader possibility for future extension.
            app["container"] = containers[0]

        return app

    @gen.coroutine
    @authenticated
    def retrieve_collection(self, qs, **kwargs):
        """Retrieves a dictionary containing the image and the associated
        container, if active, as values."""
        accs = self.application.db.get_accounting_for_user(
            self.current_user.account)

        result = []
        size = len(accs)
        for entry in accs:
            try:
                obj = yield self.retrieve_object(entry.id)
            except exceptions.ObjectNotFound:
                continue

            result.append(obj)

        return result, size


class ApplicationList(ResourceList):
    schema = ApplicationSchema
    model_connector = ApplicationConnector


class ApplicationDetails(ResourceDetails):
    schema = ApplicationSchema
    model_connector = ApplicationConnector

