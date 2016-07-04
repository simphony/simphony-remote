import unittest
from traitlets import HasTraits, Int, Unicode

from remoteappmanager.traitlets import as_dict, set_traits_from_dict


class Classy(HasTraits):
    a = Int()
    b = Unicode()


class TestTraitlets(unittest.TestCase):
    def test_as_dict(self):
        c = Classy()
        c.a = 2
        c.b = "hello"

        res = as_dict(c)
        self.assertEqual(res, {
            "a": 2,
            "b": "hello"
        })

    def test_set_traits_from_dict(self):
        c = Classy()
        c.a = 2
        c.b = "hello"

        d = {
            "a": 5,
            "b": "world",
            "c": "this should be ignored"
        }

        set_traits_from_dict(c, d)
        self.assertEqual(c.a, 5)
        self.assertEqual(c.b, "world")
