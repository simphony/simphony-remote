from unittest.mock import Mock, patch

from tornado import web, escape, gen
import tornadowebapi
from tornadowebapi import registry
from tornadowebapi.http import httpstatus

from remoteappmanager.docker.container import Container
from remoteappmanager.docker.image import Image
from remoteappmanager.restresources import Application
from remoteappmanager.tests import utils
from remoteappmanager.tests.utils import AsyncHTTPTestCase, mock_coro_factory
from remoteappmanager.tests.mocking.dummy import create_hub


class DummyAuthenticator:
    @classmethod
    @gen.coroutine
    def authenticate(cls, handler):
        user = Mock()
        user.account = Mock()
        return user


class TestApplication(AsyncHTTPTestCase):
    def setUp(self):
        super().setUp()

    def get_app(self):
        reg = registry.Registry()
        reg.register(Application)
        reg.authenticator = DummyAuthenticator
        handlers = reg.api_handlers('/')
        app = web.Application(handlers=handlers)
        app.db = Mock()
        app.hub = create_hub()
        app.container_manager = Mock()
        app.container_manager.image = mock_coro_factory(
            return_value=Image(name="boo", ui_name="foo_ui"))
        app.container_manager.containers_from_mapping_id = mock_coro_factory(
            return_value=[])
        application_mock_1 = Mock()
        application_mock_1.image = "hello1"

        application_mock_2 = Mock()
        application_mock_2.image = "hello2"

        policy = Mock(
            allow_home=True,
            volume_source="foo",
            volume_target="bar",
            volume_mode="ro",
        )

        app.db.get_apps_for_user = Mock(return_value=[
            ("one", application_mock_1, policy),
            ("two", application_mock_2, policy),
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

            # Check if nothing is returned if no images are present
            self._app.container_manager.image = mock_coro_factory(
                return_value=None)

            res = self.fetch("/api/v1/applications/")

            self.assertEqual(res.code, httpstatus.OK)
            self.assertEqual(escape.json_decode(res.body),
                             {"items": []})

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
                             {'container': None,
                              'image': {'description': '',
                                        'icon_128': '',
                                        'name': 'boo',
                                        'ui_name': 'foo_ui',
                                        'policy': {
                                            "allow_home": True,
                                            "volume_mode": 'ro',
                                            "volume_source": "foo",
                                            "volume_target": "bar",
                                        }},
                              'mapping_id': 'one'})

            self._app.container_manager.containers_from_mapping_id = \
                mock_coro_factory(return_value=[Container(
                    name="container",
                    image_name="xxx",
                    url_id="yyy")])

            res = self.fetch("/api/v1/applications/one/")

            self.assertEqual(res.code, httpstatus.OK)
            self.assertEqual(escape.json_decode(res.body),
                             {'container':
                                 {'image_name': 'xxx',
                                  'name': 'container',
                                  'url_id': 'yyy'},
                              'image': {'description': '',
                                        'icon_128': '',
                                        'name': 'boo',
                                        'ui_name': 'foo_ui',
                                        'policy': {
                                            "allow_home": True,
                                            "volume_mode": 'ro',
                                            "volume_source": "foo",
                                            "volume_target": "bar",
                                        }},
                              'mapping_id': 'one'})

            res = self.fetch("/api/v1/applications/three/")

            self.assertEqual(res.code, httpstatus.NOT_FOUND)

            # Check the not found case if the image is not present
            self._app.container_manager.image = mock_coro_factory(None)

            res = self.fetch("/api/v1/applications/one/")
            self.assertEqual(res.code, httpstatus.NOT_FOUND)
