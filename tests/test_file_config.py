import unittest

from remoteappmanager.file_config import FileConfig

# The arguments we pass
from tests import fixtures
from tests.utils import arguments, invocation_argv


class TestFileConfig(unittest.TestCase):
    def setUp(self):
        # We can run the application config only once. It uses a global
        # object that can't be reinitialized cleanly unless we access a private
        # member.
        self.config_file = fixtures.get("remoteappmanager_config.py")

    def test_initialization(self):
        config = FileConfig()
        config.parse_config(self.config_file)
