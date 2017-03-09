import os

import time
from tornado.testing import AsyncTestCase, gen_test

from remoteappmanager.tests.temp_mixin import TempMixin
from remoteappmanager.tests.utils import mock_coro_factory

from unittest.mock import Mock, patch

from remoteappmanager.jupyterhub.auth import GitHubWhitelistAuthenticator


class TestGithubWhiteListAuthenticator(TempMixin, AsyncTestCase):
    def setUp(self):
        self.auth = GitHubWhitelistAuthenticator()
        self.auth.authenticate = mock_coro_factory(return_value="foo")
        super().setUp()

    @gen_test
    def test_basic_auth(self):
        auth = self.auth

        response = yield auth.authenticate(Mock(), {"username": "foo"})
        self.assertEqual(response, "foo")

    @gen_test
    def test_basic_auth_with_whitelist_file(self):
        whitelist_path = os.path.join(self.tempdir, "whitelist.txt")
        with open(whitelist_path, "w") as f:
            f.write("foo\n")
            f.write("bar\n")

        auth = self.auth
        auth.whitelist_file = whitelist_path
        response = yield auth.get_authenticated_user(Mock(),
                                                     {"username": "foo"})
        self.assertEqual(response, "foo")

        # Check again to touch the code that does not trigger another load
        response = yield auth.get_authenticated_user(Mock(),
                                                     {"username": "foo"})
        self.assertEqual(response, "foo")

        # wait one second, so that we see a change in mtime.
        time.sleep(1)

        # Change the file and see if we get a different behavior
        with open(whitelist_path, "w") as f:
            f.write("bar\n")

        response = yield auth.get_authenticated_user(Mock(),
                                                     {"username": "foo"})
        self.assertEqual(response, None)

    @gen_test
    def test_basic_auth_without_whitelist_file(self):
        auth = self.auth
        auth.whitelist_file = "/does/not/exist.txt"

        response = yield auth.get_authenticated_user(Mock(),
                                                     {"username": "foo"})

        # Should be equivalent to no whitelist, so everybody allowed
        self.assertEqual(response, "foo")

    @gen_test
    def test_exception_during_read(self):
        whitelist_path = os.path.join(self.tempdir, "whitelist.txt")
        with open(whitelist_path, "w") as f:
            f.write("bar\n")

        auth = self.auth
        auth.whitelist_file = whitelist_path

        # Do the first triggering, so that we load the file content.
        response = yield auth.get_authenticated_user(Mock(),
                                                     {"username": "foo"})

        self.assertEqual(response, None)

        # Then try again with an exception occurring
        with patch("os.path.getmtime") as p:
            p.side_effect = Exception("BOOM!")

            response = yield auth.get_authenticated_user(Mock(),
                                                         {"username": "foo"})
            self.assertEqual(response, None)

    def test_dummy_setter(self):
        whitelist_path = os.path.join(self.tempdir, "whitelist.txt")
        with open(whitelist_path, "w") as f:
            f.write("bar\n")

        auth = self.auth
        auth.whitelist_file = whitelist_path
        auth.whitelist = set()
        self.assertNotEqual(auth.whitelist, set())

    def test_comment_out(self):
        whitelist_path = os.path.join(self.tempdir, "whitelist.txt")
        with open(whitelist_path, "w") as f:
            f.write("# this is a comment\n")
            f.write("foo\n")
            f.write("bar\n")

        auth = self.auth
        auth.whitelist_file = whitelist_path
        yield auth.get_authenticated_user(Mock(), {"username": "foo"})

        self.assertEqual(len(auth.whitelist), 2)
