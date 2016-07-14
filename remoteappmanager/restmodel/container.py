import os
from datetime import timedelta

from tornado import gen

from remoteappmanager.docker.docker_labels import SIMPHONY_NS
from remoteappmanager.handlers.home_handler import _wait_for_http_server_2xx
from remoteappmanager.rest import exceptions
from remoteappmanager.rest.resource import Resource
from remoteappmanager.docker.container import Container as DockerContainer
from remoteappmanager.utils import url_path_join


class Container(Resource):
    @gen.coroutine
    def create(self, representation):
        """Create the container.
        The representation should accept the application mapping id we
        want to start"""
        mapping_id = representation["mapping_id"]

        account = self.current_user.account
        all_apps = self.application.db.get_apps_for_user(account)

        choice = [(m_id, app, policy)
                  for m_id, app, policy in all_apps
                  if m_id == mapping_id]

        if not choice:
            raise exceptions.UnprocessableRepresentation

        _, app, policy = choice[0]

        container = yield self._start_container(self.current_user.name,
                                                app,
                                                policy,
                                                mapping_id)
        yield self._wait_for_container_ready(container)
        yield self.application.reverse_proxy.add_container(container)

        return container.url_id

    @gen.coroutine
    def retrieve(self, identifier):
        """Return the representation of the running container."""

        container = yield self._container_from_url_id(identifier)

        if container is None:
            raise exceptions.NotFound

        return dict(
            name=container.name,
            image_name=container.image_name
        )

    @gen.coroutine
    def delete(self, identifier):
        """Stop the container."""
        app = self.application
        container = yield self._container_from_url_id(identifier)
        if not container:
            raise exceptions.NotFound

        yield app.reverse_proxy.remove_container(container)
        yield app.container_manager.stop_and_remove_container(
            container.docker_id)

    @gen.coroutine
    def items(self):
        """"Return the list of containers we are currently running."""
        container_manager = self.application.container_manager

        apps = self.application.db.get_apps_for_user(
            self.current_user.account)

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

    @gen.coroutine
    def _start_container(self, user_name, app, policy, mapping_id):
        """Start the container. This method is a helper method that
        works with low level data and helps in issuing the request to the
        data container.

        Parameters
        ----------
        user_name : str
            the username

        app : ABCApplication
            the application to start

        policy : ABCApplicationPolicy
            The startup policy for the application

        Returns
        -------
        remoteappmanager.docker.container.Container
        """

        image_name = app.image
        mount_home = policy.allow_home
        volume_spec = (policy.volume_source,
                       policy.volume_target,
                       policy.volume_mode)

        manager = self.application.container_manager
        volumes = {}

        if mount_home:
            home_path = os.environ.get('HOME')
            if home_path:
                volumes[home_path] = {'bind': '/workspace', 'mode': 'rw'}
            else:
                self.log.warning('HOME (%s) is not available for %s',
                                 home_path, user_name)
                pass

        if None not in volume_spec:
            volume_source, volume_target, volume_mode = volume_spec
            volumes[volume_source] = {'bind': volume_target,
                                      'mode': volume_mode}

        try:
            f = manager.start_container(user_name, image_name,
                                        mapping_id, volumes)
            container = yield gen.with_timeout(
                timedelta(
                    seconds=self.application.file_config.network_timeout
                ),
                f
            )
        except gen.TimeoutError as e:
            self.log.warning(
                "{user}'s container failed to start in a reasonable time. "
                "giving up".format(user=user_name)
            )
            e.reason = 'timeout'
            raise e
        except Exception as e:
            self.log.error(
                "Unhandled error starting {user}'s "
                "container: {error}".format(user=user_name, error=e)
            )
            e.reason = 'error'
            raise e

        return container

    @gen.coroutine
    def _wait_for_container_ready(self, container):
        """ Wait until the container is ready to be connected

        Parameters
        ----------
        container: Container
           The container to be connected
        """
        # Note, we use the jupyterhub ORM server, but we don't use it for
        # any database activity.
        # Note: the end / is important. We want to get a 200 from the actual
        # websockify server, not the nginx (which presents the redirection
        # page).
        server_url = "http://{}:{}{}/".format(
            container.ip,
            container.port,
            url_path_join(self.application.command_line_config.base_url,
                          container.urlpath))

        yield _wait_for_http_server_2xx(
            server_url,
            self.application.file_config.network_timeout)
