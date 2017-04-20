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
    volume_source = Unicode()
    volume_target = Unicode()
    volume_mode = Unicode()


class Image(ResourceFragment):
    name = Unicode()
    ui_name = Unicode()
    icon_128 = Unicode()
    description = Unicode()
    policy = OneOf(Policy)
    configurables = List(Unicode)


class Application(Resource):
    image = OneOf(Image)
    mapping_id = Unicode()
    container = OneOf(Container)


class ApplicationHandler(ResourceHandler):
    resource_class = Application

    @gen.coroutine
    @authenticated
    def retrieve(self, instance):
        apps = self.application.db.get_apps_for_user(
            self.current_user.account
        )
        identifier = instance.identifier

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

        instance.fill({
            "image": {
                "name": image.name,
                "ui_name": image.ui_name,
                "icon_128": image.icon_128,
                "description": image.description,
                "policy": {
                    "allow_home": policy.allow_home,
                    "volume_source": policy.volume_source,
                    "volume_target": policy.volume_target,
                    "volume_mode": policy.volume_mode,
                },
                "configurables": [conf.tag for conf in image.configurables]
            },
            "mapping_id": identifier,
        })

        if len(containers):
            # We assume that we can only run one container only (although the
            # API considers a broader possibility for future extension.
            container = containers[0]
            instance.container = Container().fill({
                "name": container.name,
                "image_name": container.image_name,
                "url_id": container.url_id,
            })

    @gen.coroutine
    @authenticated
    def items(self, items_response):
        """Retrieves a dictionary containing the image and the associated
        container, if active, as values."""
        apps = self.application.db.get_apps_for_user(self.current_user.account)

        container_manager = self.application.container_manager

        result = []
        for mapping_id, app, policy in apps:
            if (yield container_manager.image(app.image)) is not None:
                result.append(mapping_id)

        items_response.set(result)
