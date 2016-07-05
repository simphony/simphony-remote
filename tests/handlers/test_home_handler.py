import os
from unittest import mock
import socket

import tornado.netutil
import tornado.testing
from tornado.testing import AsyncHTTPTestCase

from remoteappmanager.application import Application
from tests import utils
from tests.temp_mixin import TempMixin


# Workaround for tornado bug #1573, already fixed in master, but not yet
# available. Remove when upgrading tornado.
def _bind_unused_port(reuse_port=False):
    """Binds a server socket to an available port on localhost.

    Returns a tuple (socket, port).
    """
    sock = tornado.netutil.bind_sockets(None,
                                        '127.0.0.1',
                                        family=socket.AF_INET,
                                        reuse_port=reuse_port)[0]
    port = sock.getsockname()[1]
    return sock, port


class TestHomeHandler(TempMixin, AsyncHTTPTestCase):
    def setUp(self):
        self._old_proxy_api_token = os.environ.get("PROXY_API_TOKEN", None)
        os.environ["PROXY_API_TOKEN"] = "dummy_token"

        self._bind_unused_port_orig = tornado.testing.bind_unused_port
        tornado.testing.bind_unused_port = _bind_unused_port

        super().setUp()

    def tearDown(self):
        if self._old_proxy_api_token is not None:
            os.environ["PROXY_API_TOKEN"] = self._old_proxy_api_token
        else:
            del os.environ["PROXY_API_TOKEN"]

        tornado.testing.bind_unused_port = self._bind_unused_port_orig

        super().tearDown()

    def get_app(self):
        sqlite_file_path = os.path.join(self.tempdir, "sqlite.db")
        utils.init_sqlite_db(sqlite_file_path)

        command_line_config = utils.basic_command_line_config()
        file_config = utils.basic_file_config()
        file_config.db_url = "sqlite:///"+sqlite_file_path

        return Application(command_line_config, file_config)

    def test_home(self):
        with mock.patch("remoteappmanager"
                        ".handlers"
                        ".base_handler"
                        ".BaseHandler"
                        ".verify_token") as mock_verify_token:
            mock_verify_token.return_value = True
            res = self.fetch("/user/username/",
                             headers={
                                 "Cookie": "jupyter-hub-token-username=foo"
                             }
                             )

        self.assertEqual(res.code, 200)
        self.assertIn("Available Applications", res.body)
