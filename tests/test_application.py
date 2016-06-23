from unittest.mock import Mock

import os

from jupyterhub import orm
from tests.temp_mixin import TempMixin
from tornado import gen, testing

from remoteappmanager.application import Application
from remoteappmanager.docker.container import Container
from remoteappmanager.docker.container_manager import ContainerManager
from tests import utils


class TestApplication(TempMixin, testing.AsyncTestCase):
    def setUp(self):
        super().setUp()

        self._old_proxy_api_token = os.environ.get("PROXY_API_TOKEN", None)

        os.environ["PROXY_API_TOKEN"] = "dummy_token"

        self.sqlite_file_path = os.path.join(self.tempdir, "sqlite.db")
        utils.init_sqlite_db(self.sqlite_file_path)

        self.config = utils.basic_application_config()
        self.config.db_url = "sqlite:///"+self.sqlite_file_path

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
        self.assertEqual(abspath, "/user/username/containers/12345")

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

    def test_database_initialization(self):
        app = self.app

        self.assertIsNotNone(app.db)
        self.assertIsNotNone(app.user)

        self.assertEqual(app.user.name, "username")
        self.assertEqual(len(app.user.teams), 1)
        self.assertEqual(len(app.user.teams[0].users), 1)
        self.assertEqual(app.user.teams[0].users[0], app.user)
        self.assertEqual(app.user.teams[0].name, app.user.name)
