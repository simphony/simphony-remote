from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler


class ReregisterContainersHandler(BaseHandler):
    """This handler intercepts calls that filter through the reverse
    proxy due e.g. to crash of the reverse proxy.

    It will extract the url_id from the request, lookup if the appropriate
    container is actually running, and re-seed the reverse proxy with the
    appropriate data.
    """

    @web.authenticated
    @gen.coroutine
    def get(self, url_id):
        container_manager = self.application.container_manager

        container = yield container_manager.container_from_url_id(
            url_id)

        if container is not None:
            yield self.application.reverse_proxy.register(
                container.urlpath,
                container.host_url)

            self.redirect(self.request.uri)

        raise web.HTTPError(404)
