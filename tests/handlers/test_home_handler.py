import os
import urllib.parse
from unittest import mock

from tests import utils
from tests.mocking import dummy
from tests.temp_mixin import TempMixin


class TestHomeHandler(TempMixin, utils.AsyncHTTPTestCase):
    def setUp(self):
        self._old_proxy_api_token = os.environ.get("PROXY_API_TOKEN", None)
        os.environ["PROXY_API_TOKEN"] = "dummy_token"

        def cleanup():
            if self._old_proxy_api_token is not None:
                os.environ["PROXY_API_TOKEN"] = self._old_proxy_api_token
            else:
                del os.environ["PROXY_API_TOKEN"]

        self.addCleanup(cleanup)

        super().setUp()

    def get_app(self):
        app = dummy.create_application()
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_home(self):
        res = self.fetch("/user/username/",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         }
                         )

        self.assertEqual(res.code, 200)
        self.assertIn("Available Applications", str(res.body))

    def test_failed_auth(self):
        self._app.hub.verify_token.return_value = {}
        res = self.fetch("/user/username/",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         }
                         )

        self.assertGreaterEqual(res.code, 400)
        self.assertIn(self._app.file_config.login_url, res.effective_url)
        self.assertNotIn("Available Applications", str(res.body))

    def test_post_start(self):
        body = urllib.parse.urlencode(
            {'action': 'start',
             'mapping_id': 'mapping_id'
             }
        )

        with mock.patch("remoteappmanager"
                        ".handlers"
                        ".home_handler"
                        "._wait_for_http_server_2xx",
                        new_callable=utils.mock_coro_factory), \
            mock.patch("remoteappmanager"
                       ".handlers"
                       ".home_handler"
                       ".HomeHandler"
                       ".redirect") as redirect:

            self.assertFalse(self._app.reverse_proxy.register.called)
            self.fetch("/user/username/",
                       method="POST",
                       headers={
                                "Cookie": "jupyter-hub-token-username=foo"
                       },
                       body=body)

            self.assertTrue(self._app.reverse_proxy.register.called)
            self.assertTrue(redirect.called)

    def test_post_failed_auth(self):
        body = urllib.parse.urlencode(
            {'action': 'start',
             'mapping_id': 'mapping_id'
             }
        )

        self._app.hub.verify_token.return_value = {}

        res = self.fetch("/user/username/",
                         method="POST",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         },
                         body=body)

        self.assertGreaterEqual(res.code, 400)

    def test_post_stop(self):
        body = urllib.parse.urlencode(
            {'action': 'stop',
             'url_id': 'url_id'
             }
        )

        with mock.patch("remoteappmanager"
                        ".handlers"
                        ".home_handler"
                        ".HomeHandler"
                        ".redirect") as redirect:

            self.fetch("/user/username/",
                       method="POST",
                       headers={
                           "Cookie": "jupyter-hub-token-username=foo"
                       },
                       body=body)

            self.assertTrue(self._app.reverse_proxy.unregister.called)
            self.assertTrue(redirect.called)

    def test_post_view(self):
        body = urllib.parse.urlencode(
            {'action': 'view',
             'url_id': 'url_id'
             }
        )

        with mock.patch("remoteappmanager"
                        ".handlers"
                        ".home_handler"
                        "._wait_for_http_server_2xx",
                        new_callable=utils.mock_coro_factory), \
                mock.patch("remoteappmanager"
                           ".handlers"
                           ".home_handler"
                           ".HomeHandler"
                           ".redirect") as redirect:

            self.fetch("/user/username/",
                       method="POST",
                       headers={
                           "Cookie": "jupyter-hub-token-username=foo"
                       },
                       body=body)

            self.assertTrue(self._app.reverse_proxy.register.called)
            self.assertTrue(redirect.called)

    def test_container_manager_does_not_return_container(self):
        self._app.container_manager.container_from_url_id = \
            utils.mock_coro_factory(None)
        res = self.fetch(
            "/user/username/",
            method="POST",
            headers={
                "Cookie": "jupyter-hub-token-username=foo"
            },
            body=urllib.parse.urlencode({
                'action': 'view',
                'url_id': 'url_id'
            })
        )

        self.assertIn("ValueError", str(res.body))

        res = self.fetch(
            "/user/username/",
            method="POST",
            headers={
                "Cookie": "jupyter-hub-token-username=foo"
            },
            body=urllib.parse.urlencode({
                'action': 'stop',
                'url_id': 'url_id'
            })
        )

        self.assertIn("ValueError", str(res.body))
