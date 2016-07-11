import os
import unittest
import subprocess
from unittest import mock

from click.testing import CliRunner

from remoteappmanager.cli.remoteappdb import __main__ as remoteappdb
from remoteappmanager.cli.remoteappdb.__main__ import RemoteAppDBContext
from tests.temp_mixin import TempMixin
from tests.utils import mock_docker_client


def _context_factory(*args, **kwargs):
    """ Return a factory for creating RemoteAppDBContext
    with the given arguments and keyword arguments
    """
    def main_context(*args, **kwargs):
        return RemoteAppDBContext(*args, **kwargs)
    return main_context


def mock_context(*args, **kwargs):
    """ Mock the RemoteAppDBContext in the click script
    with the given arguments and keyword arguments
    """
    context_factory = _context_factory(*args, **kwargs)
    return mock.patch(
        'remoteappmanager.cli.remoteappdb.__main__.RemoteAppDBContext',
        context_factory)


class TestRemoteAppDbCLI(TempMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.db = os.path.join(self.tempdir, "test.db")
        subprocess.check_output(
            ("remoteappdb --db="+self.db+" init").split()
        )

    def _remoteappdb(self, argstring):
        return subprocess.check_output(
            ("remoteappdb --db="+self.db+" "+argstring).split()
        ).decode("utf-8")

    def test_init_command(self):
        self.assertTrue(os.path.exists(self.db))

    def test_user_create(self):
        out = self._remoteappdb("user create foo")
        self.assertEqual(out, "1\n")

        out = self._remoteappdb("user create bar")
        self.assertEqual(out, "2\n")

        out = self._remoteappdb("user list")

        self.assertIn("foo", out)
        self.assertIn("bar", out)

    def test_app_create_with_verify(self):
        runner = CliRunner()

        with mock_context(db=self.db), \
                 mock.patch('remoteappmanager.cli.remoteappdb.__main__.get_docker_client',  # noqa
                            mock_docker_client):
            # Initialise database
            runner.invoke(remoteappdb.cli, ['init'])

            # docker.client.inspect_image is mocked to always return
            # something, so verification would pass
            result = runner.invoke(remoteappdb.cli,
                                   ['app', 'create', 'anything'])

            self.assertEqual(result.exit_code, 0)

            # Check that the app is created
            result = runner.invoke(remoteappdb.cli,
                                   ['app', 'list'])
            self.assertIn('anything', result.output)

    def test_app_create_wrong_name_with_verify(self):
        runner = CliRunner()

        with mock_context(db=self.db):
            # Initialise database
            runner.invoke(remoteappdb.cli, ['init'])

            # create an application with a wrong image name
            result = runner.invoke(remoteappdb.cli,
                                   ['app', 'create', 'anything'])

            self.assertEqual(result.exit_code, 2)

            # Check that the app is not created
            result = runner.invoke(remoteappdb.cli,
                                   ['app', 'list'])
            self.assertNotIn('anything', result.output)

    def test_app_create_wrong_name_without_verify(self):
        runner = CliRunner()

        with mock_context(db=self.db):
            # Initialise database
            runner.invoke(remoteappdb.cli, ['init'])

            # create an application with a wrong image name
            result = runner.invoke(remoteappdb.cli,
                                   ['app', 'create', 'anything',
                                    '--no-verify'])

            self.assertEqual(result.exit_code, 0)

            # Check that the app is not created
            result = runner.invoke(remoteappdb.cli,
                                   ['app', 'list'])
            self.assertIn('anything', result.output)

    def test_app_grant(self):
        self._remoteappdb("app create myapp --no-verify")
        self._remoteappdb("user create user")

        out = self._remoteappdb("user list")
        self.assertNotIn("myapp", out)
        self._remoteappdb("app grant myapp user")
        self._remoteappdb("app grant myapp user "
                          "--allow-view "
                          "--volume=frobniz:froble:ro")
        out = self._remoteappdb("user list --show-apps")
        self.assertIn("myapp", out)
        self.assertIn("frobniz", out)
        self.assertIn("froble", out)
        self.assertIn(" ro\n", out)

    def test_app_revoke(self):
        self._remoteappdb("app create myapp --no-verify")
        self._remoteappdb("user create user")

        self._remoteappdb("app grant myapp user")
        self._remoteappdb("app grant myapp user --allow-view")
        out = self._remoteappdb("user list --show-apps --no-decoration")
        self.assertEqual(len(out.split('\n')), 3)
        self._remoteappdb("app revoke myapp user --revoke-all")
        out = self._remoteappdb("user list --show-apps --no-decoration")
        self.assertEqual(len(out.split('\n')), 2)
        self.assertNotIn("myapp", out)

        self._remoteappdb("app grant myapp user")
        self._remoteappdb("app grant myapp user "
                          "--allow-view")
        self._remoteappdb("app grant myapp user "
                          "--allow-view "
                          "--volume=frobniz:froble:ro")

        out = self._remoteappdb("user list --show-apps --no-decoration")
        self.assertEqual(len(out.split('\n')), 4)
        self._remoteappdb("app revoke myapp user")
        out = self._remoteappdb("user list --show-apps --no-decoration")
        self.assertEqual(len(out.split('\n')), 3)

        self._remoteappdb("app revoke myapp user --allow-view")
        out = self._remoteappdb("user list --show-apps --no-decoration")
        self.assertEqual(len(out.split('\n')), 2)
        self.assertIn("frobniz", out)
        self.assertIn("froble", out)
