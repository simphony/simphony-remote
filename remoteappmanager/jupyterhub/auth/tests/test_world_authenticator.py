from tornado.testing import AsyncTestCase, gen_test, ExpectLog
from unittest.mock import Mock

from remoteappmanager.jupyterhub.auth import WorldAuthenticator


class TestWorldAuthenticator(AsyncTestCase, ExpectLog):
    @gen_test
    def test_basic_auth(self):
        auth = WorldAuthenticator()
        response = yield auth.authenticate(Mock(), {"username": "foo"})
        self.assertEqual(response, "foo")
