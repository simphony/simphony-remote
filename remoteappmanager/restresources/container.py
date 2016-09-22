import os
from datetime import timedelta

from tornado import gen

from tornadowebapi import exceptions
from tornadowebapi.exceptions import NotFound
from tornadowebapi.resource import Resource

from remoteappmanager.utils import url_path_join
from remoteappmanager.netutils import wait_for_http_server_2xx
from traitlets import Int, HasTraits


class UnknownImageTypeStartupOptions(HasTraits):
    @classmethod
    def from_options(cls):
        return cls()

    def as_environment(self):
        return {}


class VNCAppStartupOptions(HasTraits):
    width = Int(1024)
    height = Int(768)
    depth = Int(16)

    @classmethod
    def from_options(cls, startup_options):
        return cls(width=int(startup_options["width"]),
                   height=int(startup_options["height"]))
        # We don't accept depth from the client, but we want to pass
        # the default anyway

    def as_environment(self):
        environment = {
            "X11_WIDTH": str(self.width),
            "X11_HEIGHT": str(self.height),
            "X11_DEPTH": str(self.depth),
        }
        return environment


class WebAppStartupOptions(UnknownImageTypeStartupOptions):
    pass


class Container(Resource):
    @gen.coroutine
    def create(self, representation):
        """Create the container.
        The representation should accept the application mapping id we
        want to start"""
        if self.current_user is None:
            raise NotFound()

        try:
            mapping_id = representation["mapping_id"]
        except KeyError:
            raise exceptions.BadRequest(message="missing mapping_id")

        webapp = self.application
        account = self.current_user.account
        all_apps = webapp.db.get_apps_for_user(account)

        choice = [(m_id, app, policy)
                  for m_id, app, policy in all_apps
                  if m_id == mapping_id]

        if not choice:
            self.log.warning("Could not find resource "
                             "for mapping id {}".format(mapping_id))
            raise exceptions.BadRequest(message="unrecognized mapping_id")

        _, app, policy = choice[0]

        startup_options = (yield self._extract_options_for_app(
            app,
            representation))

        # Everything is fine. Start and wait for the container to come online.
        try:
            container = yield self._start_container(
                self.current_user.name,
                app,
                policy,
                mapping_id,
                startup_options
                )
        except Exception as e:
            raise exceptions.Unable(message=str(e))

        try:
                yield self._wait_for_container_ready(container)
        except Exception as e:
            self._remove_container_noexcept(container)
            raise exceptions.Unable(message=str(e))

        urlpath = url_path_join(
            self.application.command_line_config.base_urlpath,
            container.urlpath)

        try:
            yield self.application.reverse_proxy.register(
                urlpath, container.host_url)
        except Exception as e:
            self._remove_container_noexcept(container)
            raise exceptions.Unable(message=str(e))

        return container.url_id

    @gen.coroutine
    def retrieve(self, identifier):
        """Return the representation of the running container."""
        if self.current_user is None:
            raise NotFound()

        container_manager = self.application.container_manager
        container = yield container_manager.container_from_url_id(identifier)

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
        if self.current_user is None:
            raise NotFound()

        container_manager = self.application.container_manager
        container = yield container_manager.container_from_url_id(identifier)

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
        if self.current_user is None:
            raise NotFound()

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
                         startup_options):
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

        environment = startup_options.as_environment()
        try:
            f = manager.start_container(user_name,
                                        image_name,
                                        mapping_id,
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

    @gen.coroutine
    def _extract_options_for_app(self, app, representation):
        # Get the image we want to start and check its type.
        webapp = self.application
        container_manager = webapp.container_manager

        image = yield container_manager.image(app.image)
        if image is None:
            raise exceptions.BadRequest(message="unrecognized image")

        startup_options_class = {
            "vncapp": VNCAppStartupOptions,
            "webapp": WebAppStartupOptions,
        }
        startup_options_class.get(image.type, UnknownImageTypeStartupOptions)

        try:
            startup_options = startup_options_class.from_options(
                    representation.get("startup_options", {})
            )
        except KeyError:
            raise exceptions.BadRequest(message="invalid startup_options")

        return startup_options
