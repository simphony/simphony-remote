import os
from datetime import timedelta

from tornado import gen

from tornadowebapi import exceptions
from tornadowebapi.resource import Resource

from remoteappmanager.netutils import wait_for_http_server_2xx
from remoteappmanager.webapi.decorators import authenticated


class Container(Resource):
    def validate_representation(self, representation):
        try:
            representation["mapping_id"]
        except KeyError:
            raise exceptions.BadRepresentation(message="missing mapping_id")

        return representation

    @gen.coroutine
    @authenticated
    def create(self, representation):
        """Create the container.
        The representation should accept the application mapping id we
        want to start"""

        mapping_id = representation["mapping_id"]

        webapp = self.application
        account = self.current_user.account
        all_apps = webapp.db.get_apps_for_user(account)
        container_manager = webapp.container_manager

        choice = [(m_id, app, policy)
                  for m_id, app, policy in all_apps
                  if m_id == mapping_id]

        if not choice:
            self.log.warning("Could not find resource "
                             "for mapping id {}".format(mapping_id))
            raise exceptions.BadRepresentation(
                message="unrecognized mapping_id")

        _, app, policy = choice[0]

        image = yield container_manager.image(app.image)
        if image is None:
            raise exceptions.BadRepresentation(message="unrecognized image")

        try:
            environment = self._environment_from_configurables(image,
                                                               representation)
        except Exception:
            raise exceptions.BadRepresentation(message="invalid configurables")

        # Everything is fine. Start and wait for the container to come online.
        try:
            container = yield self._start_container(
                self.current_user.name,
                app,
                policy,
                mapping_id,
                self.application.command_line_config.base_urlpath,
                environment=environment
                )
        except Exception as e:
            raise exceptions.Unable(message=str(e))

        try:
                yield self._wait_for_container_ready(container)
        except Exception as e:
            self._remove_container_noexcept(container)
            raise exceptions.Unable(message=str(e))

        try:
            yield self.application.reverse_proxy.register(
                container.urlpath,
                container.host_url)
        except Exception as e:
            self._remove_container_noexcept(container)
            raise exceptions.Unable(message=str(e))

        return container.url_id

    @gen.coroutine
    @authenticated
    def retrieve(self, identifier):
        """Return the representation of the running container."""
        container_manager = self.application.container_manager
        container = yield container_manager.find_container(
            url_id=identifier,
            user_name=self.current_user.name)

        if container is None:
            self.log.warning("Could not find container for id {}".format(
                identifier))
            raise exceptions.NotFound()

        return dict(
            name=container.name,
            image_name=container.image_name
        )

    @gen.coroutine
    @authenticated
    def delete(self, identifier):
        """Stop the container."""
        container_manager = self.application.container_manager
        container = yield container_manager.find_container(
            url_id=identifier,
            user_name=self.current_user.name
        )

        if not container:
            self.log.warning("Could not find container for id {}".format(
                             identifier))
            raise exceptions.NotFound()

        try:
            yield self.application.reverse_proxy.unregister(
                container.urlpath
            )
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
    @authenticated
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

            container = yield container_manager.find_container(
                user_name=self.current_user.name,
                mapping_id=mapping_id)

            running_containers.append(container.url_id)

        return running_containers

    ##################
    # Private

    @gen.coroutine
    def _remove_container_noexcept(self, container):
        """Removes container and silences (but logs) all exceptions
        during this circumstance."""

        # Note, can't use a context manager to perform this, because
        # context managers are only allowed to yield once
        container_manager = self.application.container_manager
        try:
            yield container_manager.stop_and_remove_container(
                container.docker_id)
        except Exception:
            self.log.exception(
                "Unable to stop container {} after "
                " failure to obtain a ready "
                "container".format(
                    container.docker_id))

    @gen.coroutine
    def _start_container(self,
                         user_name,
                         app,
                         policy,
                         mapping_id,
                         base_urlpath,
                         environment):
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

        environment: Dict
            A dictionary of envvars to pass to the container.

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
            f = manager.start_container(user_name,
                                        image_name,
                                        mapping_id,
                                        base_urlpath,
                                        volumes,
                                        environment
                                        )
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
            self.log.exception(
                "Unhandled error starting {user}'s "
                "container: {error}".format(user=user_name, error=e)
            )
            e.reason = 'error'
            raise e

        return container

    def _environment_from_configurables(self, image, representation):
        """Helper routine: extracts the configurables from the
        image, matches them to the appropriate configurables
        data in the representation, and returns the resulting environment
        """
        env = {}

        for img_conf in image.configurables:
            config_dict = representation.get(
                "configurables", {}).get(img_conf.tag, {})
            env.update(img_conf.config_dict_to_env(config_dict))

        return env

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
            container.urlpath)

        yield wait_for_http_server_2xx(
            server_url,
            self.application.file_config.network_timeout)
