from tornado.testing import AsyncTestCase, gen_test
from unittest.mock import Mock

from remoteappmanager.jupyterhub.auth import BasicAuthenticator


class TestBasicAuthenticator(AsyncTestCase):

    def setUp(self):
        self.auth = BasicAuthenticator(
            user_data={'foo': 'bar'},
            admin_data={'admin': 'password'}
        )
        super().setUp()

    @gen_test
    def test_basic_auth(self):
        response = yield self.auth.authenticate(
            Mock(), {"username": "foo", "password": 'bar'})
        self.assertEqual(response, "foo")

        response = yield self.auth.authenticate(
            Mock(), {"username": "wrong", "password": 'details'})
        self.assertIsNone(response)

    @gen_test
    def test_admin_auth(self):
        response = yield self.auth.authenticate(
            Mock(), {"username": "admin", "password": 'password'})
        self.assertEqual(response, "admin")
