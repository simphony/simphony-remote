from unittest import TestCase

from remoteappmanager.user import User


class TestUser(TestCase):

    def setUp(self):
        self.user = User(name='test-user',
                         login_service='Basic')

    def test_init(self):
        self.assertEqual('test-user', self.user.name)
        self.assertIsNone(self.user.account)
        self.assertEqual('Basic', self.user.login_service)
