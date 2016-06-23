from unittest import TestCase

from remoteappmanager.docker import docker_labels
from remoteappmanager.docker.image import Image
from tests.utils import mock_docker_client


class TestImage(TestCase):
    def test_from_docker_dict(self):
        docker_client = mock_docker_client()
        images = docker_client.images()
        image = Image.from_docker_dict(images[0])

        self.assertEqual(image.docker_id, images[0]["Id"])
        self.assertEqual(image.name, images[0]["RepoTags"][0])
        self.assertEqual(image.description,
                         images[0]["Labels"][docker_labels.DESCRIPTION])
