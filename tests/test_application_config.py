import unittest

from remoteappmanager.application_config import ApplicationConfig
from remoteappmanager.utils import with_end_slash

# The arguments we pass
from tests.utils import arguments, invocation_argv


class TestApplicationConfig(unittest.TestCase):
    def setUp(self):
        # We can run the application config only once. It uses a global
        # object that can't be reinitialized cleanly unless we access a private
        # member.
        with invocation_argv():
            self.config = ApplicationConfig()
            self.config.parse_config()

    def test_initialization(self):
        for key, value in arguments.items():
            if key == "base-url":
                value = with_end_slash(value)

            self.assertEqual(getattr(self.config, key.replace("-", "_")),
                             value)

    def test_as_dict(self):
        d = self.config.as_dict()
        self.assertIsInstance(d, dict)
        self.assertNotEqual(len(d), 0)
