import unittest
from remoteappmanager.docker.configurables import Resolution, for_image
from remoteappmanager.docker.image import Image
from remoteappmanager.tests.mocking.virtual.docker_client import \
    create_docker_client


class TestConfigurables(unittest.TestCase):
    def setUp(self):
        docker_client = create_docker_client()
        image_dict = docker_client.inspect_image('image_id2')
        self.image_2 = Image.from_docker_dict(image_dict)

        image_dict = docker_client.inspect_image('image_id1')
        self.image_1 = Image.from_docker_dict(image_dict)

    def test_resolution(self):
        self.assertTrue(Resolution.supported_by(self.image_1))
        self.assertFalse(Resolution.supported_by(self.image_2))

    def test_for_image(self):
        self.assertEqual(for_image(self.image_1), [Resolution])
        self.assertEqual(for_image(self.image_2), [])

    def test_config_dict_to_env(self):
        self.assertEqual(
            Resolution.config_dict_to_env({"resolution": "1024x768"}),
            {"X11_WIDTH": "1024",
             "X11_HEIGHT": "768",
             "X11_DEPTH": "16"
             }
        )

        with self.assertRaises(KeyError):
            Resolution.config_dict_to_env({})

        with self.assertRaises(ValueError):
            Resolution.config_dict_to_env({"resolution": "1024"})

        with self.assertRaises(ValueError):
            Resolution.config_dict_to_env({"resolution": "-10x-10"})

        with self.assertRaises(ValueError):
            Resolution.config_dict_to_env({"resolution": "0x1024"})
