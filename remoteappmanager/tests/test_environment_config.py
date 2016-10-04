import unittest
from unittest.mock import patch

from remoteappmanager.environment_config import EnvironmentConfig


class TestEnvironmentConfig(unittest.TestCase):
    def test_init(self):
        # We don't want to tinker with os.environ
        config = EnvironmentConfig()
        with patch.dict('os.environ',
                        {'JPY_API_TOKEN': 'jpy_token',
                         'PROXY_API_TOKEN': 'proxy_token'
                         }):
            config.parse_config()
            self.assertEqual(config.jpy_api_token, "jpy_token")
            self.assertEqual(config.proxy_api_token, "proxy_token")
