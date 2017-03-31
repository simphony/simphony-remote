from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler


class RegisterContainerHandler(BaseHandler):
    """This handler intercepts calls that filter through the reverse
    proxy and sets up the redirection if there's a receiving container
    accepting the connection.

    It will extract the url_id from the request, lookup if the appropriate
    container is actually running, and seed the reverse proxy with the
    appropriate data.
    """

    @web.authenticated
    @gen.coroutine
    def get(self, url_id):
        container_manager = self.application.container_manager

        container = yield container_manager.find_container(
            user_name=self.current_user.name,
            url_id=url_id)

        if container is not None:
            try:
                yield self.application.reverse_proxy.register(
                    container.urlpath,
                    container.host_url)
            except Exception:
                self.log.exception(
                    "Could not register reverse "
                    "proxy for id {} in RegisterContainerHandler".format(
                        url_id))
            else:
                self.redirect(self.request.uri)

        raise web.HTTPError(404)
