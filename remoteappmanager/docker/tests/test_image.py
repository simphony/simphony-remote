from unittest import TestCase

from remoteappmanager.docker.docker_labels import SIMPHONY_NS, SIMPHONY_NS_ENV
from remoteappmanager.docker.image import Image
from remoteappmanager.tests.mocking.virtual.docker_client import (
    create_docker_client)


class TestImage(TestCase):
    def test_from_docker_dict_images(self):
        docker_client = create_docker_client()
        image_dict = docker_client.images()[0]
        image = Image.from_docker_dict(image_dict)

        self.assertEqual(image.docker_id, image_dict["Id"])
        self.assertEqual(image.name, image_dict["RepoTags"][0])
        self.assertEqual(image.description,
                         image_dict["Labels"][SIMPHONY_NS.description])
        self.assertEqual(image.ui_name,
                         image_dict["Labels"][SIMPHONY_NS.ui_name])
        self.assertEqual(image.type, 'vncapp')

    def test_from_docker_dict_inspect_image(self):
        docker_client = create_docker_client()
        image_dict = docker_client.inspect_image('image_id1')

        labels = image_dict['Config']['Labels']
        # Insert an unpalatable label for the envs.
        labels[SIMPHONY_NS_ENV["x11-height"]+".whatever"] = None

        image = Image.from_docker_dict(image_dict)

        self.assertEqual(image.docker_id, image_dict["Id"])
        self.assertEqual(image.name, image_dict["RepoTags"][0])
        self.assertEqual(
            image.description,
            image_dict['Config']["Labels"][SIMPHONY_NS.description])
        self.assertEqual(
            image.ui_name,
            image_dict['Config']["Labels"][SIMPHONY_NS.ui_name])
        self.assertEqual(image.type, 'vncapp')
        self.assertEqual(image.env, {
            "X11_WIDTH": "",
            "X11_DEPTH": "",
            "X11_HEIGHT": "",
        })

    def test_missing_image_type(self):
        docker_client = create_docker_client()
        image_dict = docker_client.inspect_image('image_id2')
        image = Image.from_docker_dict(image_dict)

        self.assertEqual(image.type, '')
        self.assertEqual(image.env, {})
