import os
import unittest
from unittest import mock

from click.testing import CliRunner

from remoteappmanager.cli.remoteappdb import __main__ as remoteappdb
from tests.temp_mixin import TempMixin
from tests.utils import mock_docker_client


class TestRemoteAppDbCLI(TempMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.db = os.path.join(self.tempdir, "test.db")
        self._remoteappdb("init")

    def _remoteappdb(self, argstring):
        runner = CliRunner()
        result = runner.invoke(
            remoteappdb.cli,
            ("--db="+self.db+" "+argstring).split(),
            catch_exceptions=False
        )

        return result.exit_code, result.output

    def test_is_sqlitedb_url(self):
        self.assertTrue(remoteappdb.is_sqlitedb_url("sqlite://foo.db"))
        self.assertFalse(remoteappdb.is_sqlitedb_url("whatever://foo.db"))

    def test_sqlite_present(self):
        self.assertTrue(remoteappdb.sqlitedb_present(self.db))
        self.assertFalse(remoteappdb.sqlitedb_present(self.db+"whatever"))

    def test_init_command(self):
        self.assertTrue(os.path.exists(self.db))

        # This should fail because the database is already present
        exit_code, output = self._remoteappdb("init")
        self.assertNotEqual(exit_code, 0)

    def test_user_create(self):
        _, out = self._remoteappdb("user create foo")
        self.assertEqual(out, "1\n")

        _, out = self._remoteappdb("user create bar")
        self.assertEqual(out, "2\n")

        _, out = self._remoteappdb("user list")

        self.assertIn("foo", out)
        self.assertIn("bar", out)

    def test_app_create_with_verify(self):
        with mock.patch('remoteappmanager.cli.remoteappdb.__main__.get_docker_client',  # noqa
                        mock_docker_client):
            # docker.client.inspect_image is mocked to always return
            # something, so verification would pass
            exit_code, output = self._remoteappdb("app create anything")

            self.assertEqual(exit_code, 0)

            # Check that the app is created
            exit_code, output = self._remoteappdb("app list")
            self.assertIn('anything', output)

    def test_app_create_wrong_name_with_verify(self):
        # create an application with a wrong image name
        exit_code, output = self._remoteappdb('app create wrong')

        self.assertEqual(exit_code, 2)

        # Check that the app is not created
        exit_code, output = self._remoteappdb("app list")
        self.assertNotIn('wrong', output)

    def test_app_create_wrong_name_without_verify(self):
        # create an application with a wrong image name
        exit_code, output = self._remoteappdb("app create wrong2 --no-verify")

        self.assertEqual(exit_code, 0)

        # Check that the app is created
        exit_code, output = self._remoteappdb("app list")
        self.assertIn('wrong2', output)

    def test_app_grant(self):
        self._remoteappdb("app create myapp --no-verify")
        self._remoteappdb("user create user")

        _, out = self._remoteappdb("user list")
        self.assertNotIn("myapp", out)
        self._remoteappdb("app grant myapp user")
        self._remoteappdb("app grant myapp user "
                          "--allow-view "
                          "--volume=frobniz:froble:ro")
        _, out = self._remoteappdb("user list --show-apps")
        self.assertIn("myapp", out)
        self.assertIn("frobniz", out)
        self.assertIn("froble", out)
        self.assertIn(" ro\n", out)

    def test_app_revoke(self):
        self._remoteappdb("app create myapp --no-verify")
        self._remoteappdb("user create user")

        self._remoteappdb("app grant myapp user")
        self._remoteappdb("app grant myapp user --allow-view")
        _, out = self._remoteappdb("user list --show-apps --no-decoration")
        self.assertEqual(len(out.split('\n')), 3)
        self._remoteappdb("app revoke myapp user --revoke-all")
        _, out = self._remoteappdb("user list --show-apps --no-decoration")
        self.assertEqual(len(out.split('\n')), 2)
        self.assertNotIn("myapp", out)

        self._remoteappdb("app grant myapp user")
        self._remoteappdb("app grant myapp user "
                          "--allow-view")
        self._remoteappdb("app grant myapp user "
                          "--allow-view "
                          "--volume=frobniz:froble:ro")

        _, out = self._remoteappdb("user list --show-apps --no-decoration")
        self.assertEqual(len(out.split('\n')), 4)
        self._remoteappdb("app revoke myapp user")
        _, out = self._remoteappdb("user list --show-apps --no-decoration")
        self.assertEqual(len(out.split('\n')), 3)

        self._remoteappdb("app revoke myapp user --allow-view")
        _, out = self._remoteappdb("user list --show-apps --no-decoration")
        self.assertEqual(len(out.split('\n')), 2)
        self.assertIn("frobniz", out)
        self.assertIn("froble", out)

    def test_delete_user_cascade(self):
        """ Test if deleting user cascade to deleting accounting rows
        """
        # Given user is created with two accountings (application, policy)
        self._remoteappdb("app create myapp --no-verify")
        _, out = self._remoteappdb("user create user")
        self.assertEqual(out, "1\n")

        self._remoteappdb("app grant myapp user")
        self._remoteappdb("app grant myapp user --allow-view")

        _, out = self._remoteappdb("user list --show-apps --no-decoration")
        self.assertEqual(len(out.split('\n')), 3)

        # When the user is deleted, the accounting rows should be deleted
        # So when you add the user back later, those accountings should
        # not exist (This test relies on the fact that there is only one
        # user and so has the same id as before)
        self._remoteappdb("user remove user")
        _, out = self._remoteappdb("user create user")
        self.assertEqual(out, "1\n")

        _, out = self._remoteappdb("user list --show-apps --no-decoration")
        self.assertEqual(len(out.split('\n')), 2)
        self.assertNotIn("myapp", out)

    def test_delete_application_cascade(self):
        """ Test if deleting application cascade to deleting accounting rows
        """
        # Given user is created with two accountings (application, policy)
        _, out = self._remoteappdb("app create myapp --no-verify")
        self.assertEqual(out, "1\n")
        _, out = self._remoteappdb("user create user")
        self.assertEqual(out, "1\n")

        self._remoteappdb("app grant myapp user")
        self._remoteappdb("app grant myapp user --allow-view")

        _, out = self._remoteappdb("user list --show-apps --no-decoration")
        self.assertEqual(len(out.split('\n')), 3)

        # When the application is deleted, the associated accounting rows
        # should be deleted.  So when you add the application back later,
        # those accountings should not exist
        # (This test relies on the fact that there is only one app and so
        # the application row has the same id as before)
        self._remoteappdb("app remove myapp")
        _, out = self._remoteappdb("app create myapp --no-verify")
        self.assertEqual(out, "1\n")

        _, out = self._remoteappdb("user list --show-apps --no-decoration")
        self.assertEqual(len(out.split('\n')), 2)
        self.assertNotIn("myapp", out)

    def test_commands_noinit(self):
        # Remove the conveniently setup database
        os.remove(self.db)

        exit_code, out = self._remoteappdb("user create foo")
        self.assertNotEqual(exit_code, 0)

        exit_code, out = self._remoteappdb("app create foo")
        self.assertNotEqual(exit_code, 0)
