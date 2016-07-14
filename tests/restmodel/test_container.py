from unittest.mock import Mock, patch

from remoteappmanager.restmodel import Container
from tests import utils
from tornado import web, escape

from remoteappmanager import rest
from remoteappmanager.rest import registry, httpstatus

from tests.utils import AsyncHTTPTestCase, mock_coro_factory


class TestContainer(AsyncHTTPTestCase):
    def setUp(self):
        super().setUp()

    def get_app(self):
        handlers = rest.api_handlers('/')
        registry.registry.register(Container)
        app = web.Application(handlers=handlers)
        container_manager = Mock()
        container_manager.image = mock_coro_factory()
        app.container_manager = container_manager
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
        def prepare_side_effect(*args, **kwargs):
            user = Mock()
            user.account = Mock()
            args[0].current_user = user

        with patch("remoteappmanager"
                   ".handlers"
                   ".base_handler"
                   ".BaseHandler"
                   ".prepare",
                   new_callable=utils.mock_coro_new_callable(
                    side_effect=prepare_side_effect)
                   ):
            res = self.fetch("/api/v1/containers/")

            self.assertEqual(res.code, httpstatus.OK)
            self.assertEqual(escape.json_decode(res.body),
                             {"items": []})
