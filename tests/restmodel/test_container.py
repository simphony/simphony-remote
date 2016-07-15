from unittest.mock import Mock, patch

from remoteappmanager.restresources import Container
from tests import utils
from tornado import web, escape

from remoteappmanager import rest
from remoteappmanager.rest import registry, httpstatus

from tests.utils import AsyncHTTPTestCase, mock_coro_factory


class TestContainer(AsyncHTTPTestCase):
    def setUp(self):
        super().setUp()

        def prepare_side_effect(*args, **kwargs):
            user = Mock()
            user.account = Mock()
            args[0].current_user = user

        self.mock_prepare = utils.mock_coro_new_callable(
            side_effect=prepare_side_effect)

    def get_app(self):
        handlers = rest.api_handlers('/')
        registry.registry.register(Container)
        app = web.Application(handlers=handlers)
        app.file_config = Mock()
        app.file_config.network_timeout = 5
        app.command_line_config = Mock()
        app.command_line_config.base_url = "http://127.0.0.1:8000/"
        app.reverse_proxy = Mock()
        app.reverse_proxy.add_container = mock_coro_factory()
        app.reverse_proxy.remove_container = mock_coro_factory()
        container = Mock()
        container.urlpath = "containers/12345"
        container.url_id = "12345"
        app.container_manager = Mock()
        app.container_manager.image = mock_coro_factory()
        app.container_manager.start_container = mock_coro_factory(
            return_value=container)
        app.container_manager.stop_and_remove_container = mock_coro_factory()
        app.container_manager.docker_client.containers = mock_coro_factory(
            return_value=[]
        )

        app.db = Mock()
        application_mock_1 = Mock()
        application_mock_1.image = "hello1"

        application_mock_2 = Mock()
        application_mock_2.image = "hello2"
        app.db.get_apps_for_user = Mock(return_value=[
            ("one", application_mock_1, Mock()),
            ("two", application_mock_2, Mock()),
        ])
        return app

    def test_items(self):
        with patch("remoteappmanager"
                   ".handlers"
                   ".base_handler"
                   ".BaseHandler"
                   ".prepare",
                   new_callable=self.mock_prepare
                   ):
            res = self.fetch("/api/v1/containers/")

            self.assertEqual(res.code, httpstatus.OK)
            self.assertEqual(escape.json_decode(res.body),
                             {"items": []})

            # Add a mock image so that we check what happens if we do
            # have something
            self._app.container_manager.image = mock_coro_factory(
                return_value=[Mock()]
            )
            mock_container = Mock()
            mock_container.url_id = "hello"
            self._app.container_manager.containers_from_mapping_id = \
                mock_coro_factory([mock_container])

            res = self.fetch("/api/v1/containers/")

            self.assertEqual(res.code, httpstatus.OK)

            # We have two "hello" but it's an artifact of the mocking.
            # in a real application they are different, one for each
            # application+policy running
            self.assertEqual(escape.json_decode(res.body),
                             {"items": ["hello", "hello"]})

    def test_create(self):
        with patch("remoteappmanager"
                   ".handlers"
                   ".base_handler"
                   ".BaseHandler"
                   ".prepare",
                   new_callable=self.mock_prepare
                   ), \
             patch("remoteappmanager"
                   ".restresources"
                   ".container"
                   "._wait_for_http_server_2xx",
                   new_callable=utils.mock_coro_factory):

            res = self.fetch(
                "/api/v1/containers/",
                method="POST",
                body=escape.json_encode(dict(
                    mapping_id="one"
                )))

            self.assertEqual(res.code, httpstatus.CREATED)

            # The port is random due to testing env. Check if it's absolute
            self.assertIn("http://", res.headers["Location"])
            self.assertIn("/api/v1/containers/12345/", res.headers["Location"])

    def test_retrieve(self):
        with patch("remoteappmanager"
                   ".handlers"
                   ".base_handler"
                   ".BaseHandler"
                   ".prepare",
                   new_callable=self.mock_prepare
                   ):

            res = self.fetch("/api/v1/containers/notfound/")
            self.assertEqual(res.code, httpstatus.NOT_FOUND)

            self._app.container_manager.docker_client.containers = \
                mock_coro_factory(return_value=[utils.containers_dict()])

            # The url is not important. The replacement of the containers
            # method up there guarantees that the method will return
            # something, regardless of the filter used.
            res = self.fetch("/api/v1/containers/found/")
            self.assertEqual(res.code, httpstatus.OK)

            content = escape.json_decode(res.body)
            self.assertEqual(content["image_name"],
                             "simphony/app:simphony-framework-mayavi")
            self.assertEqual(content["name"], "/cocky_pasteur")

    def test_delete(self):
        with patch("remoteappmanager"
                   ".handlers"
                   ".base_handler"
                   ".BaseHandler"
                   ".prepare",
                   new_callable=self.mock_prepare
                   ):

            res = self.fetch("/api/v1/containers/notfound/", method="DELETE")
            self.assertEqual(res.code, httpstatus.NOT_FOUND)

            self._app.container_manager.docker_client.containers = \
                mock_coro_factory(return_value=[utils.containers_dict()])

            res = self.fetch("/api/v1/containers/found/", method="DELETE")
            self.assertEqual(res.code, httpstatus.NO_CONTENT)
