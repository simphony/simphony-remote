from tornadowebapi.authenticator import NullAuthenticator
from tornadowebapi.http import httpstatus

from remoteappmanager.docker.container import Container as DockerContainer
from remoteappmanager.tests.mocking import dummy
from remoteappmanager.tests.temp_mixin import TempMixin
from remoteappmanager.tests.utils import (
    AsyncHTTPTestCase,
    mock_coro_factory)
from tornado import escape


class TestContainer(TempMixin, AsyncHTTPTestCase):
    def get_app(self):
        app = dummy.create_admin_application()
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_delete(self):
        self._app.container_manager.container_from_url_id = mock_coro_factory(
            DockerContainer(user="username")
        )
        res = self.fetch("/user/username/api/v1/containers/found/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=username"
                         })
        self.assertEqual(res.code, httpstatus.NO_CONTENT)
        self.assertTrue(self._app.reverse_proxy.unregister.called)

        self._app.container_manager.container_from_url_id = \
            mock_coro_factory(return_value=None)
        res = self.fetch("/user/username/api/v1/containers/notfound/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=username"
                         })
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_delete_failure_reverse_proxy(self):
        self._app.container_manager.container_from_url_id = mock_coro_factory(
            DockerContainer(user="username")
        )
        self._app.reverse_proxy.unregister.side_effect = Exception()

        res = self.fetch("/user/username/api/v1/containers/found/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=username"
                         })
        self.assertEqual(res.code, httpstatus.NO_CONTENT)

    def test_delete_failure_stop_container(self):
        manager = self._app.container_manager
        manager.container_from_url_id = mock_coro_factory(
            DockerContainer(user="username")
        )
        manager.stop_and_remove_container = mock_coro_factory(
            side_effect=Exception())

        res = self.fetch("/user/username/api/v1/containers/found/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=username"
                         })
        self.assertEqual(res.code, httpstatus.NO_CONTENT)

    def test_post_failed_auth(self):
        self._app.hub.verify_token.return_value = {}

        res = self.fetch("/user/username/api/v1/containers/",
                         method="POST",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         },
                         body=escape.json_encode({"mapping_id": "12345"}))

        self.assertGreaterEqual(res.code, 400)


class TestContainerNoUser(TempMixin, AsyncHTTPTestCase):
    def get_app(self):
        app = dummy.create_admin_application()
        app.registry.authenticator = NullAuthenticator
        return app

    def test_delete_no_user(self):
        res = self.fetch("/user/username/api/v1/containers/found/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         })
        self.assertEqual(res.code, httpstatus.NOT_FOUND)
