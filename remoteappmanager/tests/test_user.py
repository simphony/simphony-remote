from unittest import TestCase

from ..user import User


class TestUser(TestCase):

    def setUp(self):

        self.user = User()

    def test_demo_applications(self):

        self.assertListEqual([], self.user.demo_applications)
        self.assertListEqual(
            [],
            self.user.demo_applications
        )
