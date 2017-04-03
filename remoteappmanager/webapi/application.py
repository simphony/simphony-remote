from tornado import gen
from tornadowebapi.exceptions import NotFound
from tornadowebapi.resource import Resource

from remoteappmanager.webapi.decorators import authenticated


class Application(Resource):
    @gen.coroutine
    @authenticated
    def retrieve(self, identifier):
        apps = self.application.db.get_apps_for_user(
            self.current_user.account
        )

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

        representation = {
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
        }

        if len(containers):
            # We assume that we can only run one container only (although the
            # API considers a broader possibility for future extension.
            container = containers[0]
            representation["container"] = dict(
                name=container.name,
                image_name=container.image_name,
                url_id=container.url_id,
            )
        else:
            representation["container"] = None

        return representation

    @gen.coroutine
    @authenticated
    def items(self):
        """Retrieves a dictionary containing the image and the associated
        container, if active, as values."""
        apps = self.application.db.get_apps_for_user(self.current_user.account)

        container_manager = self.application.container_manager

        result = []
        for mapping_id, app, policy in apps:
            if (yield container_manager.image(app.image)) is not None:
                result.append(mapping_id)

        return result
