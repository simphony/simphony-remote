from unittest.mock import Mock, patch

from tornado import escape

from remoteappmanager.rest import httpstatus

from tests.utils import (AsyncHTTPTestCase, mock_coro_factory,
                         mock_coro_new_callable)
from tests.mocking import dummy
from tests.mocking.virtual.docker_client import create_docker_client


class TestContainer(AsyncHTTPTestCase):
    def setUp(self):
        super().setUp()

        def prepare_side_effect(*args, **kwargs):
            user = Mock()
            user.name = 'user_name'
            args[0].current_user = user

        self.mock_prepare = mock_coro_new_callable(
            side_effect=prepare_side_effect)

    def get_app(self):
        command_line_config = dummy.basic_command_line_config()
        command_line_config.base_urlpath = '/'
        return dummy.create_application(command_line_config)

    def test_items(self):
        with patch("remoteappmanager.handlers.base_handler.BaseHandler.prepare",   # noqa
                   new_callable=self.mock_prepare):
            res = self.fetch("/api/v1/containers/")

            self.assertEqual(res.code, httpstatus.OK)
            self.assertEqual(escape.json_decode(res.body),
                             {"items": ['url_id']})

            # We have another container running
            self._app.container_manager.docker_client._sync_client = (
                create_docker_client(
                    container_ids=('container_id1',),
                    container_labels=(
                        {'eu.simphony-project.docker.user': 'user_name',
                         'eu.simphony-project.docker.mapping_id': 'mapping_id',
                         'eu.simphony-project.docker.url_id': 'url_id1234'},)))

            res = self.fetch("/api/v1/containers/")
            self.assertEqual(res.code, httpstatus.OK)
            self.assertEqual(escape.json_decode(res.body),
                             {"items": ["url_id1234"]})

    def test_create(self):
        with patch("remoteappmanager.handlers.base_handler.BaseHandler.prepare",  # noqa
                   new_callable=self.mock_prepare), \
                patch("remoteappmanager.restresources.container._wait_for_http_server_2xx",  # noqa
                      new_callable=mock_coro_factory), \
                patch("remoteappmanager.docker.container_manager._generate_container_url_id",  # noqa
                      return_value="12345678"):

            res = self.fetch(
                "/api/v1/containers/",
                method="POST",
                body=escape.json_encode({'mapping_id': 'mapping_id'}))

            self.assertEqual(res.code, httpstatus.CREATED)

            # The port is random due to testing env. Check if it's absolute
            self.assertIn("http://", res.headers["Location"])
            self.assertIn("/api/v1/containers/12345678",
                          res.headers["Location"])

    def test_retrieve(self):
        with patch("remoteappmanager.handlers.base_handler.BaseHandler.prepare",  # noqa
                   new_callable=self.mock_prepare):

            res = self.fetch("/api/v1/containers/notfound/")
            self.assertEqual(res.code, httpstatus.NOT_FOUND)

            res = self.fetch("/api/v1/containers/url_id/")
            self.assertEqual(res.code, httpstatus.OK)

            content = escape.json_decode(res.body)
            self.assertEqual(content["image_name"], "image_name1")
            self.assertEqual(content["name"],
                             "/remoteexec-username-mapping_5Fid")

    def test_delete(self):
        with patch("remoteappmanager.handlers.base_handler.BaseHandler.prepare",  # noqa
                   new_callable=self.mock_prepare):

            res = self.fetch("/api/v1/containers/notfound/", method="DELETE")
            self.assertEqual(res.code, httpstatus.NOT_FOUND)

            res = self.fetch("/api/v1/containers/url_id/", method="DELETE")
            self.assertEqual(res.code, httpstatus.NO_CONTENT)
