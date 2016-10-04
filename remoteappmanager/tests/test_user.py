import unittest
from unittest.mock import Mock

from remoteappmanager.user import User


class TestUser(unittest.TestCase):
    def test_init(self):
        mock_account = Mock()
        mock_account.is_admin = False

        self.assertFalse(User(name="foo", account=None).is_admin)
        self.assertFalse(User(name="foo", account=mock_account).is_admin)

        mock_account.is_admin = True
        self.assertTrue(User(name="foo", account=mock_account).is_admin)
