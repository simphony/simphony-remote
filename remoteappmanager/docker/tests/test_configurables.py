import unittest
from remoteappmanager.docker.configurables import (
    Resolution, StartupData, for_image,
)
from remoteappmanager.docker.image import Image
from remoteappmanager.tests.mocking.virtual.docker_client import (
    VirtualDockerClient)


class TestConfigurables(unittest.TestCase):
    def setUp(self):
        docker_client = VirtualDockerClient.with_containers()
        image_dict = docker_client.inspect_image(
            'simphonyproject/simphony-mayavi:0.6.0')
        self.image_1 = Image.from_docker_dict(image_dict)

        image_dict = docker_client.inspect_image(
            'simphonyproject/ubuntu-image:latest')
        self.image_2 = Image.from_docker_dict(image_dict)

        image_dict = docker_client.inspect_image(
            'simphonyproject/simphony-paraview')
        self.image_3 = Image.from_docker_dict(image_dict)

    def test_resolution(self):
        self.assertTrue(Resolution.supported_by(self.image_1))
        self.assertFalse(Resolution.supported_by(self.image_2))
        self.assertTrue(Resolution.supported_by(self.image_3))

    def test_startup_data(self):
        self.assertFalse(StartupData.supported_by(self.image_1))
        self.assertFalse(StartupData.supported_by(self.image_2))
        self.assertTrue(StartupData.supported_by(self.image_3))

    def test_for_image(self):
        self.assertEqual(for_image(self.image_1), [Resolution])
        self.assertEqual(for_image(self.image_2), [])
        self.assertEqual(for_image(self.image_3), [Resolution, StartupData])

    def test_config_dict_to_env_resolution(self):
        self.assertEqual(
            Resolution.config_dict_to_env({"resolution": "1280x800"}),
            {"X11_WIDTH": "1280",
             "X11_HEIGHT": "800",
             "X11_DEPTH": "16"
             }
        )

        default = Resolution.default_env()
        self.assertEqual(default,
                         {"X11_WIDTH": "1024",
                          "X11_HEIGHT": "768",
                          "X11_DEPTH": "16"
                          }
                         )
        self.assertEqual(Resolution.config_dict_to_env(None), default)
        self.assertEqual(Resolution.config_dict_to_env({}), default)

        with self.assertRaises(ValueError):
            Resolution.config_dict_to_env({"resolution": "1024"})

        with self.assertRaises(ValueError):
            Resolution.config_dict_to_env({"resolution": "-10x-10"})

        with self.assertRaises(ValueError):
            Resolution.config_dict_to_env({"resolution": "0x1024"})

    def test_config_dict_to_env_startup_data(self):
        self.assertEqual(
            StartupData.config_dict_to_env({"srdata": "/home/test/can.ex2"}),
            {"SRDATA": "/home/test/can.ex2"}

        )

        default = StartupData.default_env()
        self.assertEqual(default, {"SRDATA": ""})
        self.assertEqual(StartupData.config_dict_to_env(None), default)
        self.assertEqual(StartupData.config_dict_to_env({}), default)

        with self.assertRaises(ValueError):
            StartupData.config_dict_to_env({"srdata": 123})
