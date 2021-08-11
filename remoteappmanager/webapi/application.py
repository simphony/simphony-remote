from tornado import gen
from tornadowebapi.exceptions import NotFound
from tornadowebapi.resource import Resource
from tornadowebapi.resource_fragment import ResourceFragment
from tornadowebapi.traitlets import Unicode, OneOf, Bool, List
from tornadowebapi.resource_handler import ResourceHandler

from remoteappmanager.webapi.decorators import authenticated


class Container(ResourceFragment):
    name = Unicode()
    image_name = Unicode()
    url_id = Unicode()


class Policy(ResourceFragment):
    app_license = Unicode(allow_none=True)
    allow_home = Bool()
    volume_source = Unicode(allow_none=True)
    volume_target = Unicode(allow_none=True)
    volume_mode = Unicode(allow_none=True)
    allow_startup_data = Bool()


class Image(ResourceFragment):
    name = Unicode()
    ui_name = Unicode()
    icon_128 = Unicode()
    description = Unicode()
    type = Unicode()
    policy = OneOf(Policy)
    configurables = List(Unicode)


class Application(Resource):
    mapping_id = Unicode(allow_empty=False, strip=True)
    image = OneOf(Image)
    container = OneOf(Container, optional=True)


class ApplicationHandler(ResourceHandler):
    resource_class = Application

    @gen.coroutine
    @authenticated
    def retrieve(self, resource, **kwargs):
        accs = self.application.db.get_accounting_for_user(
            self.current_user
        )
        identifier = resource.identifier

        # Convert the list of tuples in a dict
        accs_dict = {
            acc.id: (acc.application, acc.application_policy)
            for acc in accs}

        if identifier not in accs_dict:
            raise NotFound()

        app, policy = accs_dict[identifier]

        container_manager = self.application.container_manager
        image = yield container_manager.image(app.image)
        if image is None:
            # The user has access to an application that is no longer
            # available in docker.
            raise NotFound()

        containers = yield container_manager.find_containers(
            user_name=self.current_user.name,
            mapping_id=identifier)

        resource.mapping_id = identifier
        resource.image = Image()
        resource.image.fill({
            "name": image.name,
            "ui_name": image.ui_name,
            "icon_128": image.icon_128,
            "description": image.description,
            "type": image.type,
            "configurables": [conf.tag for conf in image.configurables]
        })
        resource.image.policy = Policy()
        resource.image.policy.fill(policy)

        if len(containers):
            # We assume that we can only run one container only (although the
            # API considers a broader possibility for future extension.
            resource.container = Container()
            resource.container.fill(containers[0])

    @gen.coroutine
    @authenticated
    def items(self, items_response, **kwargs):
        """Retrieves a dictionary containing the image and the associated
        container, if active, as values."""
        accs = self.application.db.get_accounting_for_user(
            self.current_user)

        result = []
        for entry in accs:
            resource = self.resource_class(identifier=entry.id)
            try:
                yield self.retrieve(resource)
            except NotFound:
                continue

            result.append(resource)

        items_response.set(result)
