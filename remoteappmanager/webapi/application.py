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
    allow_home = Bool()
    volume_source = Unicode(allow_none=True)
    volume_target = Unicode(allow_none=True)
    volume_mode = Unicode(allow_none=True)


class Image(ResourceFragment):
    name = Unicode()
    ui_name = Unicode()
    icon_128 = Unicode()
    description = Unicode()
    policy = OneOf(Policy)
    configurables = List(Unicode)


class Application(Resource):
    image = OneOf(Image)
    container = OneOf(Container, optional=True)


class ApplicationHandler(ResourceHandler):
    resource_class = Application

    @gen.coroutine
    @authenticated
    def retrieve(self, resource, **kwargs):
        apps = self.application.db.get_apps_for_user(
            self.current_user.account
        )
        identifier = resource.identifier

        # Convert the list of tuples in a dict
        apps_dict = {mapping_id: (app, policy)
                     for mapping_id, app, policy in apps}

        if identifier not in apps_dict:
            raise NotFound()

        app, policy = apps_dict[identifier]

        container_manager = self.application.container_manager
        image = yield container_manager.image(app.image)
        if image is None:
            # The user has access to an application that is no longer
            # available in docker.
            raise NotFound()

        containers = yield container_manager.find_containers(
            user_name=self.current_user.name,
            mapping_id=identifier)

        resource.image = Image()
        resource.image.fill({
                "name": image.name,
                "ui_name": image.ui_name,
                "icon_128": image.icon_128,
                "description": image.description,
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
        apps = self.application.db.get_apps_for_user(self.current_user.account)

        result = []
        for mapping_id, _, _ in apps:
            resource = self.resource_class(identifier=mapping_id)
            try:
                yield self.retrieve(resource)
            except NotFound:
                continue

            result.append(resource)

        items_response.set(result)
