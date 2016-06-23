import os

from remoteappmanager.docker.container import Container
from remoteappmanager.docker.container_manager import ContainerManager
from tests import utils
from tornado.testing import AsyncTestCase, gen_test


class TestContainerManager(AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.manager = ContainerManager()
        self.mock_docker_client = utils.mock_docker_client()
        self.manager.docker_client.client = self.mock_docker_client

    def test_instantiation(self):
        self.assertEqual(self.manager.containers, {})
        self.assertIsNotNone(self.manager.docker_client)

    @gen_test
    def test_start_stop(self):
        mock_client = self.mock_docker_client

        result = yield self.manager.start_container("username", "imageid")
        self.assertTrue(mock_client.start.called)
        self.assertIsInstance(result, Container)
        self.assertFalse(mock_client.stop.called)
        self.assertFalse(mock_client.remove_container.called)

        yield self.manager.stop_and_remove_container(result.docker_id)

        self.assertTrue(mock_client.stop.called)
        self.assertTrue(mock_client.remove_container.called)

    @gen_test
    def test_container_for_image(self):
        result = yield self.manager.containers_for_image("imageid")
        self.assertEqual(len(result), 0)

        yield self.manager.start_container("username", "imageid")

        result = yield self.manager.containers_for_image("imageid")
        self.assertEqual(len(result), 1)

        expected = {'name': 'remoteexec-username-imageid',
                    'image_id': 'imageid',
                    'image_name': 'imageid',
                    'ip': '127.0.0.1',
                    'port': 666,
                    'docker_id': 'containerid'}

        for key, value in expected.items():
            self.assertEqual(getattr(result[0], key), value)

    @gen_test
    def test_race_condition_spawning(self):

        # Start the operations, and retrieve the future.
        # they will stop at the first yield and not go further until
        # we yield them
        f1 = self.manager.start_container("username", "imageid")
        f2 = self.manager.start_container("username", "imageid")

        # If these yielding raise a KeyError, it is because the second
        # one tries to remove the same key from the list, but it has been
        # already removed by the first one. Race condition.
        yield f1
        yield f2

        self.assertEqual(self.mock_docker_client.start.call_count, 1)

    @gen_test
    def test_start_already_present_container(self):
        mock_client = \
            utils.mock_docker_client_with_existing_stopped_container()
        self.manager.docker_client.client = mock_client

        result = yield self.manager.start_container(
            "vagrant",
            "simphony/simphony-remote-docker:simphony-framework-paraview")
        self.assertTrue(mock_client.start.called)
        self.assertIsInstance(result, Container)

        # Stop should have been called and the container removed
        self.assertTrue(mock_client.stop.called)
        self.assertTrue(mock_client.remove_container.called)

    @gen_test
    def test_start_container_with_nonexisting_volume_source(self):
        # These volume sources are invalid
        volumes = {'~no_way_this_be_valid': {'bind': '/target_vol1',
                                             'mode': 'ro'},
                   '/no_way_this_be_valid': {'bind': '/target_vol2',
                                             'mode': 'ro'}}

        # This volume source is valid
        good_path = os.path.abspath('.')
        volumes[good_path] = {'bind': '/target_vol3',
                              'mode': 'ro'}

        yield self.manager.start_container("username", "imageid", volumes)

        # Call args and keyword args that create_container receives
        args = self.manager.docker_client.client.create_container.call_args
        actual_volume_targets = args[1]['volumes']

        # Invalid volume paths should have been filtered away
        self.assertNotIn('/target_vol1', actual_volume_targets)
        self.assertNotIn('/target_vol2', actual_volume_targets)

        # Home directory is valid, should stay
        self.assertIn('/target_vol3', actual_volume_targets)
