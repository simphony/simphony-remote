import os
from tornado.testing import AsyncTestCase, gen_test

from remoteappmanager.docker.async_docker_client import AsyncDockerClient
from tests.docker.config import nonlinux_config
from tests import utils


class TestAsyncDockerClient(AsyncTestCase):
    @gen_test
    def test_info(self):
        client = AsyncDockerClient()
        client.client = utils.mock_docker_client()
        response = yield client.info()
        # Test contents of response
        self.assertIsInstance(response, dict)
        self.assertIn("ID", response)

    @gen_test
    def test_real_connection(self):
        config = None
        if "DOCKER_HOST" not in os.environ:
            config = nonlinux_config()

            if not os.path.exists(config.tls_cert):
                self.skipTest("Certificates are not available. Skipping.")

        client = AsyncDockerClient(config=config)
        response = yield client.info()
        # Test contents of response
        self.assertIsInstance(response, dict)
        self.assertIn("ID", response)
