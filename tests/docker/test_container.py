from unittest import TestCase

from remoteappmanager.docker.container import Container


class TestContainer(TestCase):
    def test_url(self):
        container = Container(
            url_id="12345"
        )

        self.assertEqual(container.url, "containers/12345")

    def test_host_url(self):
        container = Container(
            ip="123.45.67.89",
            port=31337
        )

        self.assertEqual(container.host_url, "http://123.45.67.89:31337")
