import unittest

from remoteappmanager.command_line_config import CommandLineConfig
from remoteappmanager.utils import with_end_slash

# The arguments we pass
from tests.utils import arguments, invocation_argv


class TestCommandLineConfig(unittest.TestCase):
    def setUp(self):
        # We can run the application config only once. It uses a global
        # object that can't be reinitialized cleanly unless we access a private
        # member.
        with invocation_argv():
            self.config = CommandLineConfig()
            self.config.parse_config()

    def test_initialization(self):
        for key, value in arguments.items():
            if key == "base-urlpath":
                value = with_end_slash(value)

            self.assertEqual(getattr(self.config, key.replace("-", "_")),
                             value)
