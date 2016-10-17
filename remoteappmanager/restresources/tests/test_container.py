from unittest.mock import patch

from tornadowebapi.authenticator import NullAuthenticator
from tornadowebapi.http import httpstatus

from remoteappmanager.docker.image import Image
from remoteappmanager.docker.container import Container as DockerContainer
from remoteappmanager.tests.mocking import dummy
from remoteappmanager.tests.temp_mixin import TempMixin
from remoteappmanager.tests.utils import (
    AsyncHTTPTestCase,
    mock_coro_factory,
    mock_coro_new_callable)
from tornado import escape


class TestContainer(TempMixin, AsyncHTTPTestCase):
    def get_app(self):
        app = dummy.create_application()
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def request_containers(self, body=None):
        """Utility method to reduce repetition.
        Issues a POST fetch request with the appropriately encoded body if
        given, otherwise issues a GET request."""
        kwargs = {}

        if body is not None:
            kwargs["method"] = "POST"
            kwargs["body"] = escape.json_encode(body)

        return self.fetch(
            "/user/username/api/v1/containers/",
            headers={
                "Cookie": "jupyter-hub-token-username=foo"
            },
            **kwargs
        )

    def test_items(self):
        manager = self._app.container_manager
        manager.image = mock_coro_factory(Image())
        manager.containers_from_mapping_id = mock_coro_factory(
            [DockerContainer()])

        res = self.request_containers()

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
            res = self.request_containers(dict(
                    mapping_id="mapping_id",
                    configurables={
                        "resolution": {
                            "resolution": "1024x768"
                        }
                    }
                ))

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
                       side_effect=TimeoutError("timeout"))):

            self._app.container_manager.stop_and_remove_container = \
                mock_coro_factory()
            res = self.request_containers(dict(
                    mapping_id="mapping_id",
                    configurables={
                        "resolution": {
                            "resolution": "1024x768"
                        }
                    }
                ))

            self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)
            self.assertTrue(
                self._app.container_manager.stop_and_remove_container.called)
            self.assertEqual(escape.json_decode(res.body), {
                "type": "Unable",
                "message": "timeout"})

    def test_create_fails_for_reverse_proxy_failure(self):
        with patch("remoteappmanager"
                   ".restresources"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_new_callable()):

            self._app.container_manager.stop_and_remove_container = \
                mock_coro_factory()
            self._app.reverse_proxy.register = mock_coro_factory(
                side_effect=Exception("Boom!"))

            res = self.request_containers(dict(
                    mapping_id="mapping_id",
                    configurables={
                        "resolution": {
                            "resolution": "1024x768"
                        }
                    }
                ))

            self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)
            self.assertTrue(
                self._app.container_manager.stop_and_remove_container.called)
            self.assertEqual(escape.json_decode(res.body), {
                "type": "Unable",
                "message": "Boom!"})

    def test_create_fails_for_start_container_failure(self):
        with patch("remoteappmanager"
                   ".restresources"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_new_callable()):

            self._app.container_manager.stop_and_remove_container = \
                mock_coro_factory()
            self._app.container_manager.start_container = mock_coro_factory(
                side_effect=Exception("Boom!"))

            res = self.request_containers(dict(
                    mapping_id="mapping_id",
                    configurables={
                        "resolution": {
                            "resolution": "1024x768"
                        }
                    }
                ))

            self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)
            self.assertEqual(escape.json_decode(res.body), {
                "type": "Unable",
                "message": "Boom!"})

    def test_create_fails_for_incorrect_configurable(self):
        res = self.request_containers(dict(
                mapping_id="mapping_id",
                configurables={
                    "resolution": {
                        "wooo": "dsdsa"
                    }
                }
            ))

        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

    def test_create_succeeds_for_empty_configurable(self):
        with patch("remoteappmanager"
                   ".restresources"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_new_callable()):
            res = self.request_containers(dict(
                    mapping_id="mapping_id",
                    configurables={
                        "resolution": {
                        }
                    }
                ))

            self.assertEqual(res.code, httpstatus.CREATED)

            res = self.request_containers(dict(
                    mapping_id="mapping_id",
                    configurables={
                    }
                ))

            self.assertEqual(res.code, httpstatus.CREATED)

            res = self.request_containers(dict(
                mapping_id="mapping_id",
            ))

            self.assertEqual(res.code, httpstatus.CREATED)

    def test_create_fails_for_missing_mapping_id(self):
        res = self.request_containers(dict(
                whatever="123"
            ))

        self.assertEqual(res.code, httpstatus.BAD_REQUEST)
        self.assertEqual(escape.json_decode(res.body),
                         {"type": "BadRequest",
                          "message": "missing mapping_id"})

    def test_create_fails_for_invalid_mapping_id(self):
        res = self.request_containers(
            dict(mapping_id="whatever"))

        self.assertEqual(res.code, httpstatus.BAD_REQUEST)
        self.assertEqual(escape.json_decode(res.body),
                         {"type": "BadRequest",
                          "message": "unrecognized mapping_id"})

    def test_retrieve(self):
        self._app.container_manager.container_from_url_id = mock_coro_factory(
            DockerContainer(user="username")
        )
        res = self.fetch("/user/username/api/v1/containers/found/",
                         headers={
                             "Cookie": "jupyter-hub-token-username=username"
                         })
        self.assertEqual(res.code, httpstatus.OK)

        content = escape.json_decode(res.body)
        self.assertEqual(content["image_name"], "")
        self.assertEqual(content["name"], "")

        self._app.container_manager.container_from_url_id = \
            mock_coro_factory(return_value=None)
        res = self.fetch("/user/username/api/v1/containers/notfound/",
                         headers={
                             "Cookie": "jupyter-hub-token-username=username"
                         })
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_prevent_retrieve_from_other_user(self):
        self._app.container_manager.container_from_url_id = mock_coro_factory(
            DockerContainer(user="foo")
        )
        res = self.fetch("/user/username/api/v1/containers/found/",
                         headers={
                             "Cookie": "jupyter-hub-token-username=username"
                         })
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

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

    def test_prevent_delete_from_other_user(self):
        self._app.container_manager.container_from_url_id = mock_coro_factory(
            DockerContainer(user="foo")
        )
        res = self.fetch("/user/username/api/v1/containers/found/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=username"
                         })
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_post_start(self):
        with patch("remoteappmanager"
                   ".restresources"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_factory):
            self._app.container_manager.containers_from_mapping_id = \
                mock_coro_factory(return_value=[DockerContainer()])

            self.assertFalse(self._app.reverse_proxy.register.called)
            self.fetch("/user/username/api/v1/containers/",
                       method="POST",
                       headers={
                                "Cookie": "jupyter-hub-token-username=foo"
                       },
                       body=escape.json_encode({
                           "mapping_id": "mapping_id",
                           "configurables": {
                                "resolution": {
                                    "resolution": "1024x768"
                                }
                           }
                       }))

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


class TestContainerNoUser(TempMixin, AsyncHTTPTestCase):
    def get_app(self):
        app = dummy.create_application()
        app.registry.authenticator = NullAuthenticator
        return app

    def test_items_no_user(self):
        res = self.fetch(
            "/user/username/api/v1/containers/",
            headers={
                "Cookie": "jupyter-hub-token-username=foo"
            },
        )
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_create_no_user(self):
        res = self.fetch(
            "/user/username/api/v1/containers/",
            method="POST",
            headers={
                "Cookie": "jupyter-hub-token-username=foo"
            },
            body=escape.json_encode(dict(
                mapping_id="mapping_id"
            )))

        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_delete_no_user(self):
        res = self.fetch("/user/username/api/v1/containers/found/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         })
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_retrieve_no_user(self):
        res = self.fetch("/user/username/api/v1/containers/found/",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         })
        self.assertEqual(res.code, httpstatus.NOT_FOUND)
