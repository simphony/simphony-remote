from unittest.mock import Mock, patch

from remoteappmanager.restmodel import Application
from tests import utils
from tornado import web, escape

from remoteappmanager import rest
from remoteappmanager.rest import registry, httpstatus

from tests.utils import AsyncHTTPTestCase


class TestApplication(AsyncHTTPTestCase):
    def setUp(self):
        super().setUp()

    def get_app(self):
        handlers = rest.api_handlers('/')
        registry.registry.register(Application)
        app = web.Application(handlers=handlers)
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
            res = self.fetch("/api/v1/applications/")

            self.assertEqual(res.code, httpstatus.OK)
            self.assertEqual(escape.json_decode(res.body),
                             {"items": ["one", "two"]})

    def test_retrieve(self):
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
            res = self.fetch("/api/v1/applications/one/")

            self.assertEqual(res.code, httpstatus.OK)
            self.assertEqual(escape.json_decode(res.body),
                             {"image": "hello1"})

            res = self.fetch("/api/v1/applications/two/")

            self.assertEqual(res.code, httpstatus.OK)
            self.assertEqual(escape.json_decode(res.body),
                             {"image": "hello2"})

            res = self.fetch("/api/v1/applications/three/")

            self.assertEqual(res.code, httpstatus.NOT_FOUND)
