import socket
import os
import uuid
from datetime import timedelta

import errno

from remoteappmanager.utils import url_path_join
from tornado import gen, ioloop, web
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.log import app_log

from remoteappmanager.handlers.base_handler import BaseHandler


class HomeHandler(BaseHandler):
    """Render the user's home page"""

    @web.authenticated
    @gen.coroutine
    def get(self):
        images_info = yield self._get_images_info()
        self.render('home.html', images_info=images_info)

    @web.authenticated
    @gen.coroutine
    def post(self):
        """POST spawns with user-specified options"""
        options = self._parse_form()

        try:
            action = options["action"][0]

            # Hardcode handlers on the user-submitted form key. We don't want
            # to risk weird injections
            handler = {
                "start": self._actionhandler_start,
                "stop": self._actionhandler_stop,
                "view": self._actionhandler_view
            }[action]
        except (KeyError, IndexError):
            self.log.error("Failed to retrieve action from form.",
                           exc_info=True)
            return

        try:
            yield handler(options)
        except Exception as e:
            # Create a random reference number for support
            ref = str(uuid.uuid1())
            self.log.exception("Failed with POST action: {0}. {1} "
                               "Ref: {2}".format(
                                   action, str(e), ref))

            images_info = yield self._get_images_info()

            # Render the home page again with the error message
            # User-facing error message (less info)
            message = ('Failed to {action}. '
                       'Reason: {error_type} '
                       '(Ref: {ref})')
            self.render('home.html',
                        images_info=images_info,
                        error_message=message.format(
                            action=action,
                            error_type=type(e).__name__,
                            ref=ref))

    # Subhandling after post

    @gen.coroutine
    def _actionhandler_start(self, options):
        """Sub handling. Acts in response to a "start" request from
        the user."""
        container_manager = self.application.container_manager

        mapping_id = options["mapping_id"][0]

        all_apps = self.application.db.get_apps_for_user(
            self.current_user.account)

        choice = [(m_id, app, policy)
                  for m_id, app, policy in all_apps
                  if m_id == mapping_id]

        if not choice:
            raise ValueError("User is not allowed to run the application.")

        _, app, policy = choice[0]

        container = None
        user_name = self.current_user.name
        try:
            container = yield self._start_container(user_name,
                                                    app,
                                                    policy,
                                                    mapping_id)
            yield self._wait_for_container_ready(container)
        except Exception as e:
            # Clean up, if the container is running
            if container is not None:
                try:
                    yield container_manager.stop_and_remove_container(
                        container.docker_id)
                except Exception:
                    self.log.exception(
                        "Unable to stop container {} after failure"
                        " to obtain a ready container".format(
                            container.docker_id)
                    )
            raise e

        # The server is up and running. Now contact the proxy and add
        # the container url to it.
        url = yield self.application.reverse_proxy.add_container(container)

        # Redirect the user
        self.log.info('Redirecting to {}'.format(url))
        self.redirect(url)

    @gen.coroutine
    def _actionhandler_view(self, options):
        """Redirects to an already started container.
        It is not different from pasting the appropriate URL in the
        web browser, but we validate the container id first.
        """
        url_id = options["url_id"][0]

        container_manager = self.application.container_manager
        container = yield container_manager.container_from_url_id(url_id)
        if not container:
            self.finish("Unable to view the application")
            return

        # make sure the container is actually running and working
        yield self._wait_for_container_ready(container)

        # in case the reverse proxy is not already set up
        url = yield self.application.reverse_proxy.add_container(container)

        self.log.info('Redirecting to {}'.format(url))
        self.redirect(url)

    @gen.coroutine
    def _actionhandler_stop(self, options):
        """Stops a running container.
        """
        url_id = options["url_id"][0]

        app = self.application
        container_manager = app.container_manager

        container = yield container_manager.container_from_url_id(url_id)
        if not container:
            self.finish("Unable to view the application")
            return

        try:
            yield app.reverse_proxy.remove_container(container)
        except HTTPError as http_error:
            # The reverse proxy may be absent to start with
            if http_error.code != 404:
                raise http_error

        yield container_manager.stop_and_remove_container(container.docker_id)

        # We don't have fancy stuff at the moment to change the button, so
        # we just reload the page.
        self.redirect(self.application.command_line_config.base_url)

    # private

    @gen.coroutine
    def _get_images_info(self):
        """Retrieves a dictionary containing the image and the associated
        container, if active, as values."""
        container_manager = self.application.container_manager

        apps = self.application.db.get_apps_for_user(
            self.current_user.account)

        images_info = []

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
            container = None
            if len(containers):
                container = containers[0]

            images_info.append({
                "image": image,
                "mapping_id": mapping_id,
                "container": container
            })
        return images_info

    @gen.coroutine
    def _start_container(self, user_name, app, policy, mapping_id):
        """Start the container. This method is a helper method that
        works with low level data and helps in issuing the request to the
        data container.

        Parameters
        ----------
        user_name : str
            the user name to be associated with the container

        app : ABCApplication
            the application to start

        policy : ABCApplicationPolicy
            The startup policy for the application

        Returns
        -------
        Container
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

    def _parse_form(self):
        """Extract the form options from the form and return them
        in a practical dictionary."""
        form_options = {}
        for key, byte_list in self.request.body_arguments.items():
            form_options[key] = [bs.decode('utf8') for bs in byte_list]

        return form_options

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


@gen.coroutine
def _wait_for_http_server_2xx(url, timeout=10):
    """Wait for an HTTP Server to respond at url and respond with a 2xx code.
    """
    loop = ioloop.IOLoop.current()
    tic = loop.time()
    client = AsyncHTTPClient()

    while loop.time() - tic < timeout:
        try:
            response = yield client.fetch(url, follow_redirects=True)
        except HTTPError as e:
            # Skip code 599 because it's expected and we don't want to
            # pollute the logs.
            if e.code != 599:
                app_log.warning("Server at %s responded with: %s", url, e.code)
        except (OSError, socket.error) as e:
            if e.errno not in {errno.ECONNABORTED,
                               errno.ECONNREFUSED,
                               errno.ECONNRESET}:
                app_log.warning("Failed to connect to %s (%s)", url, e)
        except Exception as e:
            # In case of any unexpected exception, we just log it and keep
            # trying until eventually we timeout.
            app_log.warning("Unknown exception occurred connecting to "
                            "%s (%s)", url, e)
        else:
            app_log.info("Server at %s responded with: %s", url, response.code)
            return

        yield gen.sleep(0.1)

    raise TimeoutError("Server at {} didn't respond in {} seconds".format(
        url, timeout))
