import unittest

from remoteappmanager.rest.registry import Registry
from remoteappmanager.rest.resource import Resource


class Student(Resource):
    """Let the basic pluralization do its job"""
    pass


class Sheep(Resource):
    """Sheep plural is the same as singular."""
    __collection_name__ = "sheep"
    pass


class TestRegistry(unittest.TestCase):
    def test_instantiation(self):
        reg = Registry()

        # Register the classes.
        reg.register(Student)
        reg.register(Sheep)

        # Check if they are there with the appropriate form
        self.assertIn("students", reg)
        self.assertIn("sheep", reg)
        self.assertEqual(reg["students"], Student)
        self.assertEqual(reg["sheep"], Sheep)
