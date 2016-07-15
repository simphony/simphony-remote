import os
import urllib.parse
from unittest import mock

from remoteappmanager.db.interfaces import ABCAccounting
from remoteappmanager.docker.container import Container
from remoteappmanager.docker.container_manager import ContainerManager
from remoteappmanager.docker.image import Image
from remoteappmanager.services.hub import Hub
from remoteappmanager.services.reverse_proxy import ReverseProxy

from remoteappmanager.application import Application
from tests import utils
from tests.temp_mixin import TempMixin


class TestHomeHandler(TempMixin, utils.AsyncHTTPTestCase):
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
        sqlite_file_path = os.path.join(self.tempdir, "sqlite.db")
        utils.init_sqlite_db(sqlite_file_path)

        command_line_config = utils.basic_command_line_config()
        file_config = utils.basic_file_config()
        file_config.accounting_kwargs = {'url': "sqlite:///"+sqlite_file_path}

        app = Application(command_line_config, file_config)
        app.reverse_proxy = mock.Mock(spec=ReverseProxy)
        app.reverse_proxy.add_container = utils.mock_coro_factory("/")
        app.reverse_proxy.remove_container = utils.mock_coro_factory()
        app.hub = mock.Mock(spec=Hub)
        app.hub.verify_token = utils.mock_coro_factory({
            'pending': None,
            'name': command_line_config.user,
            'admin': False,
            'server': command_line_config.base_url})
        app.db = mock.Mock(spec=ABCAccounting)
        app.container_manager = mock.Mock(spec=ContainerManager)
        app.container_manager.start_container = \
            utils.mock_coro_factory(Container())
        app.container_manager.image = utils.mock_coro_factory(Image)
        app.container_manager.containers_from_mapping_id = \
            utils.mock_coro_factory([Container()])
        app.container_manager.container_from_url_id = \
            utils.mock_coro_factory(Container())
        app.container_manager.stop_and_remove_container = \
            utils.mock_coro_factory()

        mock_application = mock.Mock()
        mock_policy = mock.Mock()
        app.db.get_apps_for_user.return_value = (("12345",
                                                  mock_application,
                                                  mock_policy,
                                                  ),)
        return app

    def test_home(self):
        res = self.fetch("/user/username/",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         }
                         )

        self.assertEqual(res.code, 200)
        self.assertIn("Available Applications", str(res.body))

    def test_failed_auth(self):
        self._app.hub.verify_token.return_value = {}
        res = self.fetch("/user/username/",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         }
                         )

        self.assertGreaterEqual(res.code, 400)
        self.assertIn(self._app.file_config.login_url, res.effective_url)
        self.assertNotIn("Available Applications", str(res.body))

    def test_post_start(self):
        body = urllib.parse.urlencode(
            {'action': 'start',
             'mapping_id': '12345'
             }
        )

        with mock.patch("remoteappmanager"
                        ".handlers"
                        ".home_handler"
                        "._wait_for_http_server_2xx",
                        new_callable=utils.mock_coro_factory), \
            mock.patch("remoteappmanager"
                       ".handlers"
                       ".home_handler"
                       ".HomeHandler"
                       ".redirect") as redirect:

            self.assertFalse(self._app.reverse_proxy.add_container.called)
            self.fetch("/user/username/",
                       method="POST",
                       headers={
                                "Cookie": "jupyter-hub-token-username=foo"
                       },
                       body=body)

            self.assertTrue(self._app.reverse_proxy.add_container.called)
            self.assertTrue(redirect.called)

    def test_post_failed_auth(self):
        body = urllib.parse.urlencode(
            {'action': 'start',
             'mapping_id': '12345'
             }
        )

        self._app.hub.verify_token.return_value = {}

        res = self.fetch("/user/username/",
                         method="POST",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         },
                         body=body)

        self.assertGreaterEqual(res.code, 400)

    def test_post_stop(self):
        body = urllib.parse.urlencode(
            {'action': 'stop',
             'url_id': '12345'
             }
        )

        with mock.patch("remoteappmanager"
                        ".handlers"
                        ".home_handler"
                        ".HomeHandler"
                        ".redirect") as redirect:

            self.fetch("/user/username/",
                       method="POST",
                       headers={
                           "Cookie": "jupyter-hub-token-username=foo"
                       },
                       body=body)

            self.assertTrue(self._app.reverse_proxy.remove_container.called)
            self.assertTrue(redirect.called)

    def test_post_view(self):
        body = urllib.parse.urlencode(
            {'action': 'view',
             'url_id': '12345'
             }
        )

        with mock.patch("remoteappmanager"
                        ".handlers"
                        ".home_handler"
                        "._wait_for_http_server_2xx",
                        new_callable=utils.mock_coro_factory), \
                mock.patch("remoteappmanager"
                           ".handlers"
                           ".home_handler"
                           ".HomeHandler"
                           ".redirect") as redirect:

            self.fetch("/user/username/",
                       method="POST",
                       headers={
                           "Cookie": "jupyter-hub-token-username=foo"
                       },
                       body=body)

            self.assertTrue(self._app.reverse_proxy.add_container.called)
            self.assertTrue(redirect.called)
