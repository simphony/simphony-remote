from unittest import TestCase

from remoteappmanager import utils


class TestUtils(TestCase):
    def test_parse_volume_string(self):
        self.assertEqual(utils.parse_volume_string("/foo:/bar:ro"),
                         ("/foo", "/bar", "ro"))

        self.assertEqual(utils.parse_volume_string("/foo:/bar:rw"),
                         ("/foo", "/bar", "rw"))

        with self.assertRaises(ValueError):
            utils.parse_volume_string("asdzcvcxb")

        with self.assertRaises(ValueError):
            utils.parse_volume_string("/foo:/bar:xc")

    def test_mergedocs(self):
        class Base:
            def foo(self):
                """one"""

        @utils.mergedocs(Base)
        class Derived(Base):
            def foo(self):
                """two"""

        self.assertEqual(Derived.foo.__doc__, "one\ntwo")

    def test_remove_quotes(self):
        self.assertEqual(utils.remove_quotes('"foo bar"'), "foo bar")
        self.assertEqual(utils.remove_quotes('foo'), "foo")
        self.assertEqual(utils.remove_quotes('f'), "f")
        self.assertEqual(utils.remove_quotes(''), "")
        self.assertEqual(utils.remove_quotes('"'), '"')
