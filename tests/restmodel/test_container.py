import os
from unittest.mock import patch

from remoteappmanager.rest.http import httpstatus
from remoteappmanager.docker.container import Container as DockerContainer
from tests.mocking import dummy
from tests.temp_mixin import TempMixin
from tests.utils import (AsyncHTTPTestCase, mock_coro_factory,
                         mock_coro_new_callable)
from tornado import escape


class TestContainerApplication(TempMixin, AsyncHTTPTestCase):
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

    def test_items(self):
        res = self.fetch(
            "/user/username/api/v1/containers/",
            headers={
                "Cookie": "jupyter-hub-token-username=foo"
            },
        )

        self.assertEqual(res.code, httpstatus.OK)

        self.assertEqual(escape.json_decode(res.body),
                         {"items": ["", ""]})

    def test_create(self):
        with patch("remoteappmanager"
                   ".restresources"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_new_callable()):

            manager = self._app.container_manager
            manager.start_container = mock_coro_factory(DockerContainer(
                url_id="3456"
            ))
            res = self.fetch(
                "/user/username/api/v1/containers/",
                method="POST",
                headers={
                    "Cookie": "jupyter-hub-token-username=foo"
                },
                body=escape.json_encode(dict(
                    mapping_id="12345"
                )))

            self.assertEqual(res.code, httpstatus.CREATED)

            # The port is random due to testing env. Check if it's absolute
            self.assertIn("http://", res.headers["Location"])
            self.assertIn("/api/v1/containers/3456/", res.headers["Location"])

    def test_create_fails(self):
        with patch("remoteappmanager"
                   ".restresources"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_new_callable(
                       side_effect=TimeoutError())):

            res = self.fetch(
                "/user/username/api/v1/containers/",
                method="POST",
                headers={
                    "Cookie": "jupyter-hub-token-username=foo"
                },
                body=escape.json_encode(dict(
                    mapping_id="12345"
                )))

            self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)
            self.assertTrue(
                self._app.container_manager.stop_and_remove_container.called)

    def test_create_fails_for_missing_mapping_id(self):
        res = self.fetch(
            "/user/username/api/v1/containers/",
            method="POST",
            headers={
                "Cookie": "jupyter-hub-token-username=foo"
            },
            body=escape.json_encode(dict(
                whatever="123"
            )))

        self.assertEqual(res.code, httpstatus.BAD_REQUEST)
        self.assertEqual(escape.json_decode(res.body),
                         {"type": "BadRequest",
                          "message": "missing mapping_id"})

    def test_create_fails_for_invalid_mapping_id(self):
        res = self.fetch(
            "/user/username/api/v1/containers/",
            method="POST",
            headers={
                "Cookie": "jupyter-hub-token-username=foo"
            },
            body=escape.json_encode(dict(
                mapping_id="whatever"
            )))

        self.assertEqual(res.code, httpstatus.BAD_REQUEST)
        self.assertEqual(escape.json_decode(res.body),
                         {"type": "BadRequest",
                          "message": "unrecognized mapping_id"})

    def test_retrieve(self):
        res = self.fetch("/user/username/api/v1/containers/found/",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         })
        self.assertEqual(res.code, httpstatus.OK)

        content = escape.json_decode(res.body)
        self.assertEqual(content["image_name"], "")
        self.assertEqual(content["name"], "")

        self._app.container_manager.container_from_url_id = \
            mock_coro_factory(return_value=None)
        res = self.fetch("/user/username/api/v1/containers/notfound/",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         })
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_delete(self):
        res = self.fetch("/user/username/api/v1/containers/found/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         })
        self.assertEqual(res.code, httpstatus.NO_CONTENT)

        self._app.container_manager.container_from_url_id = \
            mock_coro_factory(return_value=None)
        res = self.fetch("/user/username/api/v1/containers/notfound/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         })
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_post_start(self):
        with patch("remoteappmanager"
                   ".restresources"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_factory):

            self.assertFalse(self._app.reverse_proxy.register.called)
            self.fetch("/user/username/api/v1/containers/",
                       method="POST",
                       headers={
                                "Cookie": "jupyter-hub-token-username=foo"
                       },
                       body=escape.json_encode({"mapping_id": "12345"}))

            self.assertTrue(self._app.reverse_proxy.register.called)

    def test_post_failed_auth(self):
        self._app.hub.verify_token.return_value = {}

        res = self.fetch("/user/username/api/v1/containers/",
                         method="POST",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         },
                         body=escape.json_encode({"mapping_id": "12345"}))

        self.assertGreaterEqual(res.code, 400)

    def test_stop(self):
        self.fetch("/user/username/api/v1/containers/12345/",
                   method="DELETE",
                   headers={
                      "Cookie": "jupyter-hub-token-username=foo"
                   })

        self.assertTrue(self._app.reverse_proxy.unregister.called)
