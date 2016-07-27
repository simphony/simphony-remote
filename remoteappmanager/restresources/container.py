import contextlib
import os
from datetime import timedelta

from tornado import gen

from remoteappmanager.docker.docker_labels import SIMPHONY_NS
from remoteappmanager.rest import exceptions
from remoteappmanager.rest.resource import Resource
from remoteappmanager.docker.container import Container as DockerContainer
from remoteappmanager.utils import url_path_join
from remoteappmanager.netutils import wait_for_http_server_2xx


class Container(Resource):
    @gen.coroutine
    def create(self, representation):
        """Create the container.
        The representation should accept the application mapping id we
        want to start"""
        try:
            mapping_id = representation["mapping_id"]
        except KeyError:
            raise exceptions.BadRequest(message="missing mapping_id")

        account = self.current_user.account
        all_apps = self.application.db.get_apps_for_user(account)

        choice = [(m_id, app, policy)
                  for m_id, app, policy in all_apps
                  if m_id == mapping_id]

        if not choice:
            self.log.warning("Could not find resource "
                             "for mapping id {}".format(mapping_id))
            raise exceptions.BadRequest(message="unrecognized mapping_id")

        _, app, policy = choice[0]

        try:
            container = yield self._start_container(
                self.current_user.name,
                app,
                policy,
                mapping_id)
        except Exception as e:
            raise exceptions.Unable(message=str(e))

        try:
            with self._remove_container_on_error(container):
                yield self._wait_for_container_ready(container)
        except Exception as e:
            raise exceptions.Unable(message=str(e))

        urlpath = url_path_join(
            self.application.command_line_config.base_urlpath,
            container.urlpath)

        try:
            with self._remove_container_on_error(container):
                yield self.application.reverse_proxy.register(
                    urlpath, container.host_url)
        except Exception as e:
            raise exceptions.Unable(message=str(e))

        return container.url_id

    @gen.coroutine
    def retrieve(self, identifier):
        """Return the representation of the running container."""
        container = yield self._container_from_url_id(identifier)

        if container is None:
            self.log.warning("Could not find container for id {}".format(
                identifier))
            raise exceptions.NotFound()

        return dict(
            name=container.name,
            image_name=container.image_name
        )

    @gen.coroutine
    def delete(self, identifier):
        """Stop the container."""
        container = yield self._container_from_url_id(identifier)
        container_manager = self.application.container_manager

        if not container:
            self.log.warning("Could not find container for id {}".format(
                             identifier))
            raise exceptions.NotFound()

        urlpath = url_path_join(
            self.application.command_line_config.base_urlpath,
            container.urlpath)

        try:
            yield self.application.reverse_proxy.unregister(urlpath)
        except Exception:
            # If we can't remove the reverse proxy, we cannot do much more
            # than log the problem and keep going, because we want to stop
            # the container regardless.
            self.log.exception("Could not remove reverse "
                               "proxy for id {}".format(identifier))

        try:
            yield container_manager.stop_and_remove_container(
                container.docker_id)
        except Exception:
            self.log.exception("Could not stop and remove container "
                               "for id {}".format(identifier))

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

    ##################
    # Private

    @contextlib.contextmanager
    def _remove_container_on_error(self, container):
        """Context manager that guarantees we remove the container
        if something goes wrong during the context-held operation"""
        container_manager = self.application.container_manager
        try:
            yield
        except Exception as e:
            try:
                yield container_manager.stop_and_remove_container(
                    container.docker_id)
            except Exception:
                self.log.exception(
                    "Unable to stop container {} after "
                    " failure to obtain a ready "
                    "container".format(
                        container.docker_id))
            raise e

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

        return DockerContainer.from_docker_dict(container_dict[0])

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
        container: docker.Container
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
            url_path_join(self.application.command_line_config.base_urlpath,
                          container.urlpath))

        yield wait_for_http_server_2xx(
            server_url,
            self.application.file_config.network_timeout)
