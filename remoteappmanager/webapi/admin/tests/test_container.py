from tornadowebapi.authenticator import NullAuthenticator
from tornadowebapi.http import httpstatus

from remoteappmanager.tests.webapi_test_case import WebAPITestCase
from remoteappmanager.docker.container import Container as DockerContainer
from remoteappmanager.tests.mocking import dummy
from remoteappmanager.tests.utils import mock_coro_factory


class TestContainer(WebAPITestCase):
    def get_app(self):
        app = dummy.create_admin_application()
        app.hub.get_user.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_delete(self):
        self._app.container_manager.find_container = mock_coro_factory(
            DockerContainer(user="johndoe")
        )
        self.delete("/user/johndoe/api/v1/containers/found/",
                    httpstatus.NO_CONTENT)

        self.assertTrue(self._app.reverse_proxy.unregister.called)

        self._app.container_manager.find_container = \
            mock_coro_factory(return_value=None)
        self.delete("/user/johndoe/api/v1/containers/notfound/",
                    httpstatus.NOT_FOUND)

    def test_delete_failure_reverse_proxy(self):
        self._app.container_manager.find_container = mock_coro_factory(
            DockerContainer(user="johndoe")
        )
        self._app.reverse_proxy.unregister.side_effect = Exception("BOOM!")

        self.delete("/user/johndoe/api/v1/containers/found/",
                    httpstatus.NO_CONTENT)

    def test_delete_failure_stop_container(self):
        manager = self._app.container_manager
        manager.find_container = mock_coro_factory(
            DockerContainer(user="johndoe")
        )
        manager.stop_and_remove_container = mock_coro_factory(
            side_effect=Exception("BOOM!"))

        self.delete("/user/johndoe/api/v1/containers/found/",
                    httpstatus.NO_CONTENT)

    def test_items(self):
        response, data = self.get("/user/johndoe/api/v1/containers/",
                                  httpstatus.OK)

        self.assertEqual(len(data["identifiers"]), 1)

    def cookie_auth_token(self):
        return "jupyter-hub-token-johndoe=johndoe"


class TestContainerNoUser(WebAPITestCase):
    def get_app(self):
        app = dummy.create_admin_application()
        app.registry.authenticator = NullAuthenticator
        return app

    def test_delete_no_user(self):
        self.delete("/user/johndoe/api/v1/containers/found/",
                    httpstatus.NOT_FOUND)

    def cookie_auth_token(self):
        return "jupyter-hub-token-johndoe=johndoe"
