from unittest.mock import patch

from remoteappmanager.tests.webapi_test_case import WebAPITestCase
from tornadowebapi.authenticator import NullAuthenticator
from tornadowebapi.http import httpstatus

from remoteappmanager.docker.image import Image
from remoteappmanager.docker.container import Container as DockerContainer
from remoteappmanager.tests.mocking import dummy
from remoteappmanager.tests.utils import (
    mock_coro_factory,
    mock_coro_new_callable)


class TestContainer(WebAPITestCase):
    def get_app(self):
        app = dummy.create_application()
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_items(self):
        manager = self._app.container_manager
        manager.image = mock_coro_factory(Image())
        manager.find_containers = mock_coro_factory([
                DockerContainer(user="johndoe",
                                mapping_id="whatever",
                                url_id="12345",
                                name="container",
                                image_name="image")
                ])

        code, data = self.get(
            "/user/johndoe/api/v1/containers/",
            httpstatus.OK)

        # We get two because we have two mapping ids, hence the find_containers
        # gets called once per each mapping id.
        # This is a kind of unusual case, because we only get one item
        # in the items list, due to the nature of the test.
        self.assertEqual(
            data,
            {'identifiers': ['12345', '12345'],
             'total': 2,
             'offset': 0,
             'items': {
                 '12345': {
                     'image_name': 'image',
                     'name': 'container',
                     'mapping_id': 'whatever'
                 }
             }})

    def test_items_with_none_container(self):
        manager = self._app.container_manager
        manager.image = mock_coro_factory(Image())
        manager.find_container = mock_coro_factory(None)

        code, data = self.get("/user/johndoe/api/v1/containers/",
                              httpstatus.OK)

        # We get two because we have two mapping ids, hence the find_containers
        # gets called once per each mapping id.
        # This is a kind of unusual case, because we only get one item
        # in the items list, due to the nature of the test.
        self.assertEqual(
            data,
            {
                'identifiers': [],
                'total': 0,
                'offset': 0,
                'items': {}
            }
        )

    def test_create(self):
        with patch("remoteappmanager"
                   ".webapi"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_new_callable()):

            manager = self._app.container_manager
            manager.start_container = mock_coro_factory(DockerContainer(
                url_id="3456"
            ))
            self.post(
                "/user/johndoe/api/v1/containers/",
                dict(
                    mapping_id="cbaee2e8ef414f9fb0f1c97416b8aa6c",
                    configurables={
                        "resolution": {
                            "resolution": "1024x768"
                        }
                    }
                ),
                httpstatus.CREATED
            )

    def test_create_fails(self):
        with patch("remoteappmanager"
                   ".webapi"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_new_callable(
                       side_effect=TimeoutError("timeout"))):

            self._app.container_manager.stop_and_remove_container = \
                mock_coro_factory()
            _, data = self.post(
                "/user/johndoe/api/v1/containers/",
                dict(
                    mapping_id="cbaee2e8ef414f9fb0f1c97416b8aa6c",
                    configurables={
                        "resolution": {
                            "resolution": "1024x768"
                        }
                    }
                ),
                httpstatus.INTERNAL_SERVER_ERROR
            )

            self.assertTrue(
                self._app.container_manager.stop_and_remove_container.called)
            self.assertEqual(data, {
                "type": "Unable",
                "message": "timeout"})

    def test_create_fails_for_reverse_proxy_failure(self):
        with patch("remoteappmanager"
                   ".webapi"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_new_callable()):

            self._app.container_manager.stop_and_remove_container = \
                mock_coro_factory()
            self._app.reverse_proxy.register = mock_coro_factory(
                side_effect=Exception("Boom!"))

            _, data = self.post(
                "/user/johndoe/api/v1/containers/",
                dict(
                    mapping_id="cbaee2e8ef414f9fb0f1c97416b8aa6c",
                    configurables={
                        "resolution": {
                            "resolution": "1024x768"
                        }
                    }
                ),
                httpstatus.INTERNAL_SERVER_ERROR)

            self.assertTrue(
                self._app.container_manager.stop_and_remove_container.called)
            self.assertEqual(data, {
                "type": "Unable",
                "message": "Boom!"})

    def test_create_fails_for_start_container_failure(self):
        with patch("remoteappmanager"
                   ".webapi"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_new_callable()):

            self._app.container_manager.stop_and_remove_container = \
                mock_coro_factory()
            self._app.container_manager.start_container = mock_coro_factory(
                side_effect=Exception("Boom!"))

            _, data = self.post(
                "/user/johndoe/api/v1/containers/",
                dict(
                    mapping_id="cbaee2e8ef414f9fb0f1c97416b8aa6c",
                    configurables={
                        "resolution": {
                            "resolution": "1024x768"
                        }
                    }
                ),
                httpstatus.INTERNAL_SERVER_ERROR)

            self.assertEqual(data, {
                "type": "Unable",
                "message": "Boom!"})

    def test_create_fails_for_incorrect_configurable(self):
        self.post(
            "/user/johndoe/api/v1/containers/",
            dict(
                mapping_id="cbaee2e8ef414f9fb0f1c97416b8aa6c",
                configurables={
                    "resolution": {
                        "wooo": "dsdsa"
                    }
                }
            ),
            httpstatus.BAD_REQUEST
        )

    def test_create_succeeds_for_empty_configurable(self):
        with patch("remoteappmanager"
                   ".webapi"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_new_callable()):

            self.post(
                "/user/johndoe/api/v1/containers/",
                dict(
                    mapping_id="cbaee2e8ef414f9fb0f1c97416b8aa6c",
                    image_name="image",
                    name="container",
                    configurables={
                        "resolution": {
                        }
                    }
                ),
                httpstatus.CREATED
            )

            self.post(
                "/user/johndoe/api/v1/containers/",
                dict(
                    image_name="image",
                    name="container",
                    mapping_id="cbaee2e8ef414f9fb0f1c97416b8aa6c",
                    configurables={
                    }
                ),
                httpstatus.CREATED
            )

            self.post(
                "/user/johndoe/api/v1/containers/",
                dict(
                    image_name="image",
                    name="container",
                    mapping_id="cbaee2e8ef414f9fb0f1c97416b8aa6c",
                ),
                httpstatus.CREATED
            )

    def test_create_fails_for_missing_mapping_id(self):
        _, data = self.post(
            "/user/johndoe/api/v1/containers/",
            dict(
                name="123",
                configurables={},
                image_name="456",
            ),
            httpstatus.BAD_REQUEST
        )

        self.assertEqual(
            data,
            {"type": "BadRepresentation",
             "message": "Missing mandatory elements: {'mapping_id'}"
             })

    def test_create_fails_for_invalid_mapping_id(self):
        _, data = self.post(
            "/user/johndoe/api/v1/containers/",
            dict(
                mapping_id="whatever",
                name="123",
                configurables={},
                image_name="456",
            ),
            httpstatus.BAD_REQUEST
        )

        self.assertEqual(data,
                         {"type": "BadRepresentation",
                          "message": "unrecognized mapping_id"})

    def test_retrieve(self):
        self._app.container_manager.find_container = mock_coro_factory(
            DockerContainer(user="johndoe",
                            mapping_id="whatever",
                            name="container",
                            image_name="image")
        )
        _, data = self.get("/user/johndoe/api/v1/containers/found/",
                           httpstatus.OK)

        self.assertEqual(data["image_name"], "image")
        self.assertEqual(data["name"], "container")

        self._app.container_manager.find_container = \
            mock_coro_factory(return_value=None)
        self.get("/user/johndoe/api/v1/containers/notfound/",
                 httpstatus.NOT_FOUND)

    def test_prevent_retrieve_from_other_user(self):
        self._app.container_manager.find_container = mock_coro_factory(None)

        self.get("/user/johndoe/api/v1/containers/found/",
                 httpstatus.NOT_FOUND)
        kwargs = self._app.container_manager.find_container.call_args[1]
        self.assertEqual(kwargs["user_name"], "johndoe")

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

    def test_prevent_delete_from_other_user(self):
        self._app.container_manager.find_container = mock_coro_factory(
            None
        )
        self.delete("/user/johndoe/api/v1/containers/found/",
                    httpstatus.NOT_FOUND)

        kwargs = self._app.container_manager.find_container.call_args[1]
        self.assertEqual(kwargs["user_name"], "johndoe")

    def test_post_start(self):
        with patch("remoteappmanager"
                   ".webapi"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_factory):
            self._app.container_manager.find_containers = \
                mock_coro_factory(return_value=[DockerContainer()])

            self.assertFalse(self._app.reverse_proxy.register.called)
            self.post("/user/johndoe/api/v1/containers/",
                      {
                          "mapping_id": "cbaee2e8ef414f9fb0f1c97416b8aa6c",
                          "configurables": {
                               "resolution": {
                                   "resolution": "1024x768"
                               }
                          }
                      })

            self.assertTrue(self._app.reverse_proxy.register.called)

    def test_post_failed_auth(self):
        self._app.hub.verify_token.return_value = {}

        self.post("/user/johndoe/api/v1/containers/",
                  {"mapping_id": "b7ca425a51bf40acbd305b3f782714b6"},
                  httpstatus.NOT_FOUND)

    def cookie_auth_token(self):
        return "jupyter-hub-token-johndoe=johndoe"


class TestContainerNoUser(WebAPITestCase):
    def get_app(self):
        app = dummy.create_application()
        app.registry.authenticator = NullAuthenticator
        return app

    def test_items_no_user(self):
        self.get("/user/username/api/v1/containers/",
                 httpstatus.NOT_FOUND)

    def test_create_no_user(self):
        self.post("/user/username/api/v1/containers/",
                  {"mapping_id": "mapping_id"},
                  httpstatus.NOT_FOUND)

    def test_delete_no_user(self):
        self.delete("/user/username/api/v1/containers/found/",
                    httpstatus.NOT_FOUND)

    def test_retrieve_no_user(self):
        self.get("/user/username/api/v1/containers/found/",
                 httpstatus.NOT_FOUND)

    def cookie_auth_token(self):
        return "jupyter-hub-token-username=foo"
