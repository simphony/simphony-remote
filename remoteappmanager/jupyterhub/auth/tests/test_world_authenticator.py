from tornado.testing import AsyncTestCase, gen_test
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from remoteappmanager.jupyterhub.auth import WorldAuthenticator


class TestWorldAuthenticator(AsyncTestCase):
    @gen_test
    def test_basic_auth(self):
        auth = WorldAuthenticator()
        response = yield auth.authenticate(Mock(), {"username": "foo"})
        self.assertEqual(response, "foo")
