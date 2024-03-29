import unittest
from unittest.mock import patch

from remoteappmanager.environment_config import EnvironmentConfig
from remoteappmanager.tests.utils import env_config


class TestEnvironmentConfig(unittest.TestCase):
    def test_init(self):
        # We don't want to tinker with os.environ
        config = EnvironmentConfig()
        with patch.dict('os.environ', env_config):
            config.parse_config()
            self.assertEqual(config.jpy_api_token, "jpy_token")
            self.assertEqual(config.proxy_api_token, "proxy_token")
            self.assertEqual(config.hub_host, "")
            self.assertEqual(
                config.hub_api_url, 'http://172.17.5.167:8081/hub/api')
