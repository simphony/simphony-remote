import subprocess

import os
import unittest
from unittest import mock
import pwd

from jupyterhub import orm
from remoteappmanager.spawner import Spawner
from tests import fixtures


def username():
    """Returns the current username"""
    return pwd.getpwuid(os.getuid()).pw_name


class TestSpawner(unittest.TestCase):
    def setUp(self):
        generic_server = orm.Server(
            proto="http",
            ip="127.0.0.2",
            port=31337,
            base_url="/"
        )

        api_server = orm.Server(
            proto="http",
            ip="127.0.0.1",
            port=12345,
            base_url="/foo/bar/"
        )

        mock_db = mock.Mock()
        mock_db.query = mock.Mock()
        mock_db.query().first = mock.Mock(
            return_value=orm.Proxy(
                auth_token="whatever",
                api_server=api_server
            ))
        mock_user = mock.Mock()
        mock_user.name = username()
        mock_user.state = None
        mock_user.server = generic_server

        mock_hub = orm.Hub(server=generic_server)

        self.spawner = Spawner(db=mock_db,
                               user=mock_user,
                               hub=mock_hub)

    def test_args(self):
        path = fixtures.get("remoteappmanager_config.py")
        self.spawner.config_file_path = path
        args = self.spawner.get_args()
        self.assertIn("--proxy-api-url=http://127.0.0.1:12345/foo/bar/", args)
        self.assertIn("--config-file={}".format(path), args)

    def test_cmd(self):
        self.assertEqual(self.spawner.cmd, ['remoteappmanager'])

    def test_default_config_file_path(self):
        self.assertEqual(self.spawner.config_file_path,
                         os.path.join(os.getcwd(),
                                      "remoteappmanager_config.py"))

    def test_env(self):
        env = self.spawner.get_env()
        self.assertIn("PROXY_API_TOKEN", env)
        self.assertEqual(env["PROXY_API_TOKEN"], "whatever")

    def test_cmd_spawning(self):
        env = os.environ.copy()
        env["PROXY_API_TOKEN"] = "dummy_token"
        path = fixtures.get("remoteappmanager_config.py")
        self.spawner.config_file_path = path

        args = self.spawner.get_args()

        with self.assertRaises(subprocess.TimeoutExpired):
            subprocess.check_output(
                self.spawner.cmd + args,
                timeout=2,
                env=env,
                stderr=subprocess.STDOUT)
