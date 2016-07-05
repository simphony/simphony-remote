import os
from unittest import mock

import tornado.netutil
from tornado.testing import AsyncHTTPTestCase

from remoteappmanager.application import Application
from tests import utils
from tests.temp_mixin import TempMixin
import socket


class TestHomeHandler(TempMixin, AsyncHTTPTestCase):
    def setUp(self):
        self._old_proxy_api_token = os.environ.get("PROXY_API_TOKEN", None)
        os.environ["PROXY_API_TOKEN"] = "dummy_token"
        print "XXXXXXXXXXXXXXXX"
        print(tornado.netutil.bind_sockets(
            None, 'localhost', family=socket.AF_INET, reuse_port=False))

        super().setUp()

    def tearDown(self):
        if self._old_proxy_api_token is not None:
            os.environ["PROXY_API_TOKEN"] = self._old_proxy_api_token
        else:
            del os.environ["PROXY_API_TOKEN"]

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
            res = self.fetch("/user/username/",
                             headers={
                                 "Cookie": "jupyter-hub-token-username=foo"
                             }
            )
            print(mock_verify_token.call_args)

        self.assertEqual(res.code, 200)

