import os
import unittest
import subprocess

from tests.temp_mixin import TempMixin


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

    def test_team_create(self):
        out = self._remoteappdb("team create foo")
        self.assertEqual(out, "1\n")
        out = self._remoteappdb("team create bar")
        self.assertEqual(out, "2\n")

        out = self._remoteappdb("team list")

        self.assertIn("foo", out)
        self.assertIn("bar", out)

    def test_user_has_team(self):
        self._remoteappdb("user create foo")
        out = self._remoteappdb("team list")

        self.assertIn("foo", out)

    def test_app_create(self):
        out = self._remoteappdb("app create myapp")
        self.assertEqual(out, "1\n")

        out = self._remoteappdb("app list")
        self.assertIn("myapp", out)

    def test_app_expose(self):
        self._remoteappdb("app create myapp")
        self._remoteappdb("user create user")

        out = self._remoteappdb("user list")
        self.assertNotIn("myapp", out)
        self._remoteappdb("app expose myapp user")
        out = self._remoteappdb("user list")
        self.assertIn("myapp", out)
