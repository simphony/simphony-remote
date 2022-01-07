import contextlib
import os
import pwd
import subprocess
import sys
import time
from unittest import mock

from tornado.testing import AsyncTestCase
from jupyterhub import proxy, orm, objects

from remoteappmanager.jupyterhub.spawners import (
    SystemUserSpawner,
    VirtualUserSpawner)
from remoteappmanager.tests import fixtures
from remoteappmanager.tests.temp_mixin import TempMixin


@contextlib.contextmanager
def spawner_start_and_stop(io_loop, spawner):
    try:
        io_loop.run_sync(spawner.start)
        # Wait for the process to get to the while loop
        time.sleep(1)
        yield
    finally:
        io_loop.run_sync(spawner.stop)


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
        base_url="/",
        cookie_name='cookie'
    )

    # Mock db
    db = mock.Mock()

    # Mock user
    user = mock.Mock()
    user.name = username()
    user.url = 'http://my-callback.com'
    user.admin = False
    user.state = None
    user.settings = {
        'proxy': proxy.ConfigurableHTTPProxy(
            api_url="http://127.0.0.1:12345/foo/bar/",
            auth_token="whatever"
        )
    }

    # Mock hub
    hub = objects.Hub(
        ip="127.0.0.2",
        proto="http",
        port=31337,
        base_url="/hub/",
    )

    # Mock authenticator
    authenticator = mock.Mock()
    authenticator.logout_url = mock.Mock(
        return_value='/logout_test')
    authenticator.login_service = 'TEST'

    # Mocks instantiating Spawner instance via an orm.Spawner instance
    # in the User._new_spawner method, as would happen in production
    orm_spawner = orm.Spawner(
        name='',
        server=generic_server
    )
    return spawner_class(
        db=db,
        user=user,
        orm_spawner=orm_spawner,
        hub=hub,
        authenticator=authenticator
    )


class TestSystemUserSpawner(TempMixin, AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.spawner = new_spawner(SystemUserSpawner)

    def test_args(self):
        path = fixtures.get("remoteappmanager_config.py")
        self.spawner.config_file_path = path
        args = self.spawner.get_args()
        self.assertIn("--ip=\"127.0.0.1\"", args)
        self.assertIn(f"--cookie-name=jupyter-hub-token", args)
        self.assertIn("--proxy-api-url=http://127.0.0.1:12345/foo/bar/", args)
        self.assertIn("--config-file={}".format(path), args)
        self.assertIn("--base-urlpath=\"/\"", args)

    def test_args_without_config_file_path(self):
        args = self.spawner.get_args()
        self.assertIn("--ip=\"127.0.0.1\"", args)
        self.assertIn(f"--cookie-name=jupyter-hub-token", args)
        self.assertIn("--proxy-api-url=http://127.0.0.1:12345/foo/bar/", args)
        self.assertFalse(any("--config-file=" in arg for arg in args))
        self.assertIn("--base-urlpath=\"/\"", args)

    def test_cmd(self):
        self.assertEqual(self.spawner.cmd, ['remoteappmanager'])

    def test_default_config_file_path(self):
        self.assertEqual(self.spawner.config_file_path, "")

    def test_env(self):
        env = self.spawner.get_env()
        self.assertIn("PROXY_API_TOKEN", env)
        self.assertEqual(env["PROXY_API_TOKEN"], "whatever")

    def test_env_has_docker_vars(self):
        if "DOCKER_HOST" in os.environ:
            env = self.spawner.get_env()
            self.assertIn("DOCKER_HOST", env)
            self.assertIn("DOCKER_CERT_PATH", env)
            self.assertIn("DOCKER_MACHINE_NAME", env)

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

    def test_spawner_start_and_stop_with_config_file(self):
        path = fixtures.get("remoteappmanager_config.py")
        self.spawner.config_file_path = path

        with spawner_start_and_stop(self.io_loop, self.spawner):
            status = self.io_loop.run_sync(self.spawner.poll)
            self.assertIsNone(status)

        status = self.io_loop.run_sync(self.spawner.poll)
        self.assertEqual(status, 1)

    def test_spawner_start_and_stop_without_config_file(self):
        with spawner_start_and_stop(self.io_loop, self.spawner):
            status = self.io_loop.run_sync(self.spawner.poll)
            self.assertIsNone(status)

        status = self.io_loop.run_sync(self.spawner.poll)
        self.assertEqual(status, 1)


class TestSystemUserSpawnerAsAdmin(TestSystemUserSpawner):
    # We expect the same tests above to pass.
    # admin is a full replacement application that should accept and behave
    # exactly in the same way.

    def setUp(self):
        super().setUp()
        self.spawner.user.admin = True

    def test_cmd(self):
        self.assertEqual(self.spawner.cmd, ['remoteappadmin'])


class TestVirtualUserSpawner(TestSystemUserSpawner):
    def setUp(self):
        super().setUp()
        self.spawner = new_spawner(VirtualUserSpawner)

    def test_spawner_without_workspace_dir(self):
        with spawner_start_and_stop(self.io_loop, self.spawner):
            status = self.io_loop.run_sync(self.spawner.poll)
            self.assertIsNone(status)

            # spawner.worspace_dir is not defined
            # no temporary directory is created
            self.assertFalse(os.listdir(self.tempdir))

        status = self.io_loop.run_sync(self.spawner.poll)
        self.assertEqual(status, 1)

    def test_spawner_with_workspace_dir(self):
        self.spawner.workspace_dir = self.tempdir

        with spawner_start_and_stop(self.io_loop, self.spawner):
            status = self.io_loop.run_sync(self.spawner.poll)
            self.assertIsNone(status)

            # There should be a temporary directory created
            # and it should be assigned to _virtual_workspace
            virtual_directory = self.spawner._virtual_workspace
            self.assertIn(os.path.basename(virtual_directory),
                          os.listdir(self.tempdir))

        self.assertIn(os.path.basename(virtual_directory),
                      os.listdir(self.tempdir))

        status = self.io_loop.run_sync(self.spawner.poll)
        self.assertEqual(status, 1)

    def test_spawner_with_workspace_dir_already_existent(self):
        self.spawner.workspace_dir = self.tempdir
        os.mkdir(os.path.join(self.tempdir, username()))

        with spawner_start_and_stop(self.io_loop, self.spawner):
            status = self.io_loop.run_sync(self.spawner.poll)
            self.assertIsNone(status)

            # There should be a temporary directory created
            # and it should be assigned to _virtual_workspace
            virtual_directory = self.spawner._virtual_workspace
            self.assertIn(os.path.basename(virtual_directory),
                          os.listdir(self.tempdir))

        self.assertIn(os.path.basename(virtual_directory),
                      os.listdir(self.tempdir))

    def test_spawner_with_workspace_dir_as_file(self):
        self.spawner.workspace_dir = self.tempdir

        with open(os.path.join(self.tempdir, username()), 'w'):
            pass

        with spawner_start_and_stop(self.io_loop, self.spawner):
            self.assertIsNone(self.spawner.get_env().get('HOME'))

    def test_env_has_proxy_api_token(self):
        env = self.spawner.get_env()
        self.assertIn("PROXY_API_TOKEN", env)
        self.assertEqual(env["PROXY_API_TOKEN"], "whatever")

    def test_env_has_docker_vars(self):
        if "DOCKER_HOST" in os.environ:
            env = self.spawner.get_env()
            self.assertIn("DOCKER_HOST", env)
            self.assertIn("DOCKER_CERT_PATH", env)
            self.assertIn("DOCKER_MACHINE_NAME", env)

    def test_env_has_home_if_workspace_defined(self):
        self.spawner.workspace_dir = self.tempdir

        with spawner_start_and_stop(self.io_loop, self.spawner):
            home = self.spawner.get_env().get('HOME')
            self.assertEqual(home, self.spawner._virtual_workspace)

    def test_home_not_in_env_if_workspace_undefined(self):
        with spawner_start_and_stop(self.io_loop, self.spawner):
            self.assertIsNone(self.spawner.get_env().get('HOME'))

    def test_state_if_workspace_defined(self):
        self.spawner.workspace_dir = self.tempdir

        with spawner_start_and_stop(self.io_loop, self.spawner):
            state = self.spawner.get_state()
            self.assertIn('virtual_workspace', state)
            self.assertIn(self.tempdir, state.get('virtual_workspace'))

    def test_state_if_workspace_not_defined(self):
        with spawner_start_and_stop(self.io_loop, self.spawner):
            state = self.spawner.get_state()
            self.assertNotIn('virtual_workspace', state)

    def test_start_if_workspace_path_not_exists(self):
        self.spawner.workspace_dir = '/no_way/this_exists'

        with spawner_start_and_stop(self.io_loop, self.spawner):
            # Started running
            status = self.io_loop.run_sync(self.spawner.poll)
            self.assertIsNone(status)

        # Stopped running
        status = self.io_loop.run_sync(self.spawner.poll)
        self.assertEqual(status, 1)


class TestVirtualUserSpawnerAsAdmin(TestSystemUserSpawner):
    def setUp(self):
        super().setUp()
        self.spawner.user.admin = True

    def test_cmd(self):
        self.assertEqual(self.spawner.cmd, ['remoteappadmin'])
