from tornado.testing import AsyncTestCase, ExpectLog, gen_test
from unittest.mock import Mock

from remoteappmanager.jupyterhub.auth import WorldAuthenticator


class TestWorldAuthenticator(AsyncTestCase):
    @gen_test
    def test_basic_auth(self):
        auth = WorldAuthenticator()
        log_msg = 'This authenticator authenticates everyone for testing.'
        with ExpectLog('traitlets', log_msg):
            response = yield auth.authenticate(Mock(), {"username": "foo"})
            self.assertEqual(response, "foo")
