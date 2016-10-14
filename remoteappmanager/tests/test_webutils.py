import unittest
from remoteappmanager.webutils import Link, is_link


class TestWebutils(unittest.TestCase):
    def test_link(self):
        l = Link("foo", "bar")
        self.assertTrue(is_link(l))
