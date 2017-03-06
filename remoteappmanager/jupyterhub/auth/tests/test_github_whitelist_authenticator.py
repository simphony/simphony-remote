import os

import time
from tornado.testing import AsyncTestCase, gen_test

from remoteappmanager.tests.temp_mixin import TempMixin
from remoteappmanager.tests.utils import mock_coro_factory

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from remoteappmanager.jupyterhub.auth import GitHubWhitelistAuthenticator


class TestGithubWhiteListAuthenticator(TempMixin, AsyncTestCase):
    @gen_test
    def test_basic_auth(self):
        auth = GitHubWhitelistAuthenticator()
        auth.authenticate = mock_coro_factory(return_value="foo")

        response = yield auth.authenticate(Mock(), {"username": "foo"})
        self.assertEqual(response, "foo")

    @gen_test
    def test_basic_auth_with_whitelist_file(self):
        whitelist_path = os.path.join(self.tempdir, "whitelist.txt")
        with open(whitelist_path, "w") as f:
            f.write("foo\n")
            f.write("bar\n")

        auth = GitHubWhitelistAuthenticator()
        auth.authenticate = mock_coro_factory(return_value="foo")
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
