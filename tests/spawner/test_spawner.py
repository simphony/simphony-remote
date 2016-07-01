import contextlib
import os
import pwd
import shutil
import subprocess
import sys
import time
import tempfile
import unittest
from unittest import mock

from tornado.ioloop import IOLoop
from jupyterhub import orm

from remoteappmanager.spawner import Spawner, VirtualUserSpawner
from tests import fixtures


def start_spawner(spawner):
    io_loop = IOLoop.current()
    io_loop.run_sync(spawner.start)
    # Wait for the process to get to the while loop
    time.sleep(1)


def stop_spawner(spawner):
    io_loop = IOLoop.current()
    io_loop.run_sync(spawner.stop)


@contextlib.contextmanager
def spawner_start_and_stop(spawner):
    try:
        start_spawner(spawner)
        yield
    finally:
        stop_spawner(spawner)


def username():
    """Returns the current username"""
    return pwd.getpwuid(os.getuid()).pw_name


def new_spawner(spawner_class):
    """ Create a new spawner from a given Spawner class
    """
    # Server for the user and the hub
    generic_server = orm.Server(
        proto="http",
        ip="127.0.0.2",
        port=31337,
        base_url="/"
    )

    # Mock db
    db = mock.Mock()
    db.query = mock.Mock()
    db.query().first = mock.Mock(
        return_value=orm.Proxy(
            auth_token="whatever",
            api_server=orm.Server(proto="http",
                                  ip="127.0.0.1",
                                  port=12345,
                                  base_url="/foo/bar/")))

    # Mock user
    user = mock.Mock()
    user.name = username()
    user.state = None
    user.server = generic_server

    # Mock hub
    hub = orm.Hub(server=generic_server)

    return spawner_class(db=db, user=user, hub=hub)


class TestSpawner(unittest.TestCase):
    def setUp(self):
        self.spawner = new_spawner(Spawner)

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

        try:
            with self.assertRaises(subprocess.TimeoutExpired):
                subprocess.check_output(
                    self.spawner.cmd + args,
                    timeout=2,
                    env=env,
                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            print("Output of the command:\n\n{}".format(
                exc.output.decode(sys.getdefaultencoding())))
            raise

    def test_spawner_start_and_stop(self):
        path = fixtures.get("remoteappmanager_config.py")
        self.spawner.config_file_path = path

        io_loop = IOLoop.current()

        with spawner_start_and_stop(self.spawner):
            status = io_loop.run_sync(self.spawner.poll)
            self.assertIsNone(status)

        status = io_loop.run_sync(self.spawner.poll)
        self.assertEqual(status, 1)


class TestVirtualUserSpawner(unittest.TestCase):
    def setUp(self):
        self.spawner = new_spawner(VirtualUserSpawner)
        path = fixtures.get("remoteappmanager_config.py")
        self.spawner.config_file_path = path

        # temporary directory for creating workspaces
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(self.clean_up_temp_dir)

    def clean_up_temp_dir(self):
        shutil.rmtree(self.temp_dir)

    def test_spawner_without_workspace_dir(self):
        io_loop = IOLoop.current()

        with spawner_start_and_stop(self.spawner):
            status = io_loop.run_sync(self.spawner.poll)
            self.assertIsNone(status)

            # spawner.worspace_dir is not defined
            # no temporary directory is created
            self.assertFalse(os.listdir(self.temp_dir))

        status = io_loop.run_sync(self.spawner.poll)
        self.assertEqual(status, 1)

    def test_spawner_with_workspace_dir(self):
        self.spawner.workspace_dir = self.temp_dir

        io_loop = IOLoop.current()

        with spawner_start_and_stop(self.spawner):
            status = io_loop.run_sync(self.spawner.poll)
            self.assertIsNone(status)

            # There should be a temporary directory created
            # and it should be assigned to _virtual_workspace
            virtual_directory = self.spawner._virtual_workspace
            self.assertIn(os.path.basename(virtual_directory),
                          os.listdir(self.temp_dir))

        # The temporary directory should be removed upon stop
        self.assertFalse(os.listdir(self.temp_dir))

        status = io_loop.run_sync(self.spawner.poll)
        self.assertEqual(status, 1)

    def test_env_has_proxy_api_token(self):
        env = self.spawner.get_env()
        self.assertIn("PROXY_API_TOKEN", env)
        self.assertEqual(env["PROXY_API_TOKEN"], "whatever")

    def test_env_has_home_if_workspace_defined(self):
        self.spawner.workspace_dir = self.temp_dir

        with spawner_start_and_stop(self.spawner):
            home = self.spawner.get_env().get('HOME')
            self.assertEqual(home, self.spawner._virtual_workspace)

    def test_home_not_in_env_if_workspace_undefined(self):
        with spawner_start_and_stop(self.spawner):
            self.assertIsNone(self.spawner.get_env().get('HOME'))

    def test_state_if_workspace_defined(self):
        self.spawner.workspace_dir = self.temp_dir

        with spawner_start_and_stop(self.spawner):
            state = self.spawner.get_state()
            self.assertIn('virtual_workspace', state)
            self.assertIn(self.temp_dir, state.get('virtual_workspace'))

    def test_state_if_workspace_not_defined(self):
        with spawner_start_and_stop(self.spawner):
            state = self.spawner.get_state()
            self.assertNotIn('virtual_workspace', state)

    def test_clean_up_temporary_dir_if_start_fails(self):
        self.spawner.workspace_dir = self.temp_dir

        # mock LocalProcessSpawner.start to fail
        def start_fail(instance):
            raise Exception

        with mock.patch('jupyterhub.spawner.LocalProcessSpawner.start',
                        start_fail), \
                self.assertRaises(Exception), \
                spawner_start_and_stop(self.spawner):
            pass

        # The temporary directory should be cleaned up
        self.assertFalse(os.listdir(self.temp_dir))
