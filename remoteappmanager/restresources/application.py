from remoteappmanager.rest.exceptions import NotFound
from remoteappmanager.rest.resource import Resource
from tornado import gen


class Application(Resource):
    @gen.coroutine
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

        containers = yield container_manager.containers_from_mapping_id(
            self.current_user.name,
            identifier)

        representation = {
            "image": {
                "name": image.name,
                "ui_name": image.ui_name,
                "icon_128": image.icon_128,
                "description": image.description,
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
