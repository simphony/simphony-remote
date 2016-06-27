from collections import namedtuple
import socket
import os
import uuid
from datetime import timedelta

import errno

from tornado import gen, ioloop
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.log import app_log

from remoteappmanager.handlers.base_handler import BaseHandler


# FIXME: replace these with ORM objects
# Assumed one volume per application
Volume = namedtuple('Volume', ('target', 'source', 'mode'))
Application = namedtuple('Application', ('image_name', 'volume'))


class HomeHandler(BaseHandler):
    """Render the user's home page"""

    @gen.coroutine
    def _get_images_info(self):
        container_manager = self.application.container_manager

        images_info = []
        all_images = yield container_manager.all_images()

        for image in all_images:
            containers = yield container_manager.containers_for_image(
                image.docker_id)
            container = (containers[0] if len(containers) > 0 else None)
            # For now we assume we have only one.
            images_info.append({
                "image": image,
                "container": container
            })
        return images_info

    @gen.coroutine
    def get(self):
        images_info = yield self._get_images_info()
        self.render('home.html', images_info=images_info)

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

        yield handler(self.current_user, options)

    # Subhandling after post

    @gen.coroutine
    def _actionhandler_start(self, user_name, options):
        """Sub handling. Acts in response to a "start" request from
        the user."""
        # Start the single-user server

        ref = str(uuid.uuid1())

        try:
            image_name = options["image_name"][0]
        except (IndexError, KeyError):
            message = ('Failed to start image. Reason: Failed to '
                       'retrieve image name from options.'
                       '(Ref: {ref})')
            self.render('home.html', error_message=message.format(ref=ref))
            return

        try:
            container = yield self._start_container(user_name, image_name)
        except Exception as e:
            # Create a random reference number for support
            self.log.exception("Failed to spawn docker image. %s "
                               "Ref: %s",
                               str(e), ref)

            images_info = yield self._get_images_info()

            # Render the home page again with the error message
            # User-facing error message (less info)
            message = ('Failed to start "{image_name}". Reason: {error_type} '
                       '(Ref: {ref})')
            self.render('home.html', images_info=images_info,
                        error_message=message.format(
                            image_name=image_name,
                            error_type=type(e).__name__,
                            ref=ref))
        else:
            # The server is up and running. Now contact the proxy and add
            # the container url to it.
            self.application.reverse_proxy_add_container(container)

            # Redirect the user
            url = self.application.container_url_abspath(container)
            self.log.info('Redirecting to ' + url)
            self.redirect(url)

    @gen.coroutine
    def _actionhandler_view(self, user, options):
        """Redirects to an already started container.
        It is not different from pasting the appropriate URL in the
        web browser, but we validate the container id first.
        """
        container = self._container_from_options(options)
        if not container:
            return

        url = self.application.container_url_abspath(container)
        self.log.info('Redirecting to ' + url)
        self.redirect(url)

    @gen.coroutine
    def _actionhandler_stop(self, user, options):
        """Stops a running container.
        """
        app = self.application
        container_manager = app.container_manager

        container = self._container_from_options(options)
        if not container:
            return

        yield app.reverse_proxy_remove_container(container)
        yield container_manager.stop_and_remove_container(container.docker_id)

        # We don't have fancy stuff at the moment to change the button, so
        # we just reload the page.
        self.redirect(self.application.config.base_url)

    # private

    def _container_from_options(self, options):
        """Support routine to reduce duplication.
        Retrieves and returns the container if valid and present.
        If not present, performs the http response and returns None.
        """

        container_manager = self.application.container_manager
        try:
            container_id = options["container_id"][0]
        except (KeyError, IndexError):
            self.log.exception(
                "Failed to retrieve valid container_id from form"
            )
            self.finish("Unable to retrieve valid container_id value")
            return None

        try:
            container = container_manager.containers[container_id]
        except KeyError:
            self.log.error("Unable to find container_id {} in manager".format(
                container_id))
            self.finish("Unable to find specified container_id")
            return None

        return container

    @gen.coroutine
    def _start_container(self, user_name, image_name):
        """Start the container"""
        manager = self.application.container_manager

        # Volumes to be mounted
        volumes = {}

        # FIXME: Should retrieve this info from the database
        allow_home = True

        if allow_home:
            home_path = os.path.expanduser('~'+user_name)
            volumes[home_path] = {'bind': '/workspace', 'mode': 'rw'}

        # FIXME: Should retrieve allow_common and app from the database
        allow_common = True
        app = Application(image_name=image_name,
                          # Made-up for now
                          volume=Volume(source='/appdata/image_name/common',
                                        target='/appdata',
                                        mode='ro'))

        if allow_common:
            volumes[app.volume.source] = {'bind': app.volume.target,
                                          'mode': app.volume.mode}

        try:
            f = manager.start_container(user_name, image_name, volumes)
            container = yield gen.with_timeout(
                timedelta(seconds=self.application.config.network_timeout), f)
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

        # Note, we use the jupyterhub ORM server, but we don't use it for
        # any database activity.
        # Note: the end / is important. We want to get a 200 from the actual
        # websockify server, not the nginx (which presents the redirection
        # page).
        server_url = "http://{}:{}{}/".format(
            container.ip,
            container.port,
            self.application.container_url_abspath(container))

        try:
            yield _wait_for_http_server_2xx(
                server_url,
                self.application.config.network_timeout)
        except TimeoutError as e:
            # Note: Using TimeoutError instead of gen.TimeoutError as above
            # is not a mistake.
            self.log.warning(
                "{user}'s container never showed up at {url} "
                "after {http_timeout} seconds. Giving up.".format(
                    user=user_name,
                    url=server_url,
                    http_timeout=self.application.config.network_timeout,
                )
            )
            e.reason = 'timeout'
            raise e
        except Exception as e:
            self.log.exception(
                "Unhandled error waiting for {user}'s server "
                "to show up at {url}: {error}".format(
                    user=user_name,
                    url=server_url,
                    error=e,
                )
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
