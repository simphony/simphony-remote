from unittest import TestCase

from remoteappmanager.docker import docker_labels
from remoteappmanager.docker.image import Image
from tests.utils import mock_docker_client


class TestImage(TestCase):
    def test_from_docker_dict(self):
        docker_client = mock_docker_client()
        image_dict = docker_client.images()[0]
        image = Image.from_docker_dict(image_dict)

        self.assertEqual(image.docker_id, image_dict["Id"])
        self.assertEqual(image.name, image_dict["RepoTags"][0])
        self.assertEqual(image.description,
                         image_dict["Labels"][docker_labels.DESCRIPTION])
        self.assertEqual(image.ui_name,
                         image_dict["Labels"][docker_labels.UI_NAME])
