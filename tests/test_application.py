from unittest.mock import Mock

import os

from jupyterhub import orm
from tornado import gen, testing

from remoteappmanager.application_config import ApplicationConfig
from remoteappmanager.application import Application
from remoteappmanager.docker.container import Container
from remoteappmanager.docker.container_manager import ContainerManager


class TestApplication(testing.AsyncTestCase):
    def setUp(self):
        super().setUp()

        self._old_proxy_api_token = os.environ.get("PROXY_API_TOKEN", None)

        os.environ["PROXY_API_TOKEN"] = "dummy_token"
        self.config = ApplicationConfig(
            base_url="/testing/"
        )
        self.app = Application(self.config)

    def tearDown(self):
        if self._old_proxy_api_token is not None:
            os.environ["PROXY_API_TOKEN"] = self._old_proxy_api_token
        else:
            del os.environ["PROXY_API_TOKEN"]

        super().tearDown()

    def test_initialization(self):
        app = self.app
        self.assertIsNotNone(app.config)

        # Test the configuration options
        self.assertIsNotNone(app.config.port)
        self.assertIsInstance(app.container_manager, ContainerManager)
        self.assertIsInstance(app.reverse_proxy, orm.Proxy)

    def test_container_url_abspath(self):
        app = self.app
        container = Container(docker_id="12345")
        abspath = app.container_url_abspath(container)
        self.assertEqual(abspath, "/testing/containers/12345")

    @testing.gen_test
    def test_reverse_proxy_operations(self):
        coroutine_out = None

        @gen.coroutine
        def mock_api_request(self, *args, **kwargs):
            nonlocal coroutine_out
            yield gen.sleep(0.1)
            coroutine_out = dict(args=args, kwargs=kwargs)

        app = self.app
        app.reverse_proxy = Mock(spec=orm.Proxy)
        app.reverse_proxy.api_request = mock_api_request

        container = Container(docker_id="12345")
        yield app.reverse_proxy_add_container(container)

        self.assertEqual(coroutine_out["kwargs"]["method"], "POST")

        yield app.reverse_proxy_remove_container(container)

        self.assertEqual(coroutine_out["kwargs"]["method"], "DELETE")
