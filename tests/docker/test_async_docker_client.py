import os
import sys
import warnings
from tornado.testing import AsyncTestCase, gen_test

from remoteappmanager.docker.async_docker_client import AsyncDockerClient
from tests.docker.config import nonlinux_config
from tests import utils


class TestAsyncDockerClient(AsyncTestCase):
    def setUp(self):
        super().setUp()
        # Due to a python requests design choice, we receive a warning about
        # leaking connection. This is expected and pretty much out of our
        # authority but it can be annoying in tests, hence we suppress the
        # warning. See issue simphony-remote/10
        warnings.filterwarnings(action="ignore",
                                message="unclosed",
                                category=ResourceWarning)

    def tearDown(self):
        super().tearDown()
        warnings.filterwarnings(action="default",
                                message="unclosed",
                                category=ResourceWarning)

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

        if "DOCKER_HOST" not in os.environ and sys.platform != 'linux':
            config = nonlinux_config()

            if not os.path.exists(config.tls_cert):
                self.skipTest("Certificates are not available. Skipping.")

        client = AsyncDockerClient(config=config)
        response = yield client.info()
        # Test contents of response
        self.assertIsInstance(response, dict)
        self.assertIn("ID", response)
