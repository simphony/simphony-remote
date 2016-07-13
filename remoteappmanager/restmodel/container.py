from remoteappmanager.docker.docker_labels import SIMPHONY_NS
from remoteappmanager.rest import exceptions
from remoteappmanager.rest.resource import Resource
from remoteappmanager.docker.container import Container as DockerContainer
from tornado import gen


class Container(Resource):
    @gen.coroutine
    def create(self, representation):
        # This should create the container.
        # the representation should accept the application mapping id we
        # want to start
        pass

    @gen.coroutine
    def retrieve(self, identifier):
        # We should return the representation of the running container
        # with its current status

        container = yield self._container_from_url_id(identifier)

        if container is None:
            raise exceptions.NotFound

        return dict(
            name=container.name,
            image_name=container.image_name
        )

    @gen.coroutine
    def delete(self, identifier):
        """Stop the container.
        """
        app = self.application
        container = yield self._container_from_url_id(identifier)
        if not container:
            raise exceptions.NotFound

        yield app.reverse_proxy.remove_container(container)
        yield app.container_manager.stop_and_remove_container(
            container.docker_id)

    @gen.coroutine
    def items(self):
        # We should return the list of containers we are currently
        # running.
        container_manager = self.application.container_manager

        apps = self.application.db.get_apps_for_user(
            self.current_user.orm_user)

        running_containers = []

        for mapping_id, app, policy in apps:
            image = yield container_manager.image(app.image)

            if image is None:
                # The user has access to an application that is no longer
                # available in docker. We just move on.
                continue

            containers = yield container_manager.containers_from_mapping_id(
                self.current_user.name,
                mapping_id)

            # We assume that we can only run one container only (although the
            # API considers a broader possibility for future extension.
            if len(containers):
                container = containers[0]
                running_containers.append(container.url_id)

        return running_containers

    @gen.coroutine
    def _container_from_url_id(self, container_url_id):
        """Retrieves and returns the container if valid and present.

        If not present, returns None
        """

        container_manager = self.application.container_manager

        container_dict = yield container_manager.docker_client.containers(
            filters={'label': "{}={}".format(
                SIMPHONY_NS+"url_id",
                container_url_id)})

        if not container_dict:
            return None

        return DockerContainer.from_docker_containers_dict(container_dict[0])
