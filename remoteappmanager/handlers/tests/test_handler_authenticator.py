from unittest import mock
from tornado.testing import AsyncTestCase, gen_test

from remoteappmanager.handlers.handler_authenticator import Authenticator


class TestHandlerAuthenticator(AsyncTestCase):
    @gen_test
    def test_base_authenticator(self):
        auth = Authenticator()
        result = yield auth.authenticate(mock.Mock())
        self.assertIsNone(result)

    # HubAuthenticator covered by higher level tests.
