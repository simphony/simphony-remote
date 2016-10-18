import os
from unittest import mock

from tornado.testing import AsyncTestCase, gen_test

from remoteappmanager.docker.container import Container
from remoteappmanager.docker.docker_labels import SIMPHONY_NS_RUNINFO
from remoteappmanager.docker.container_manager import ContainerManager, \
    OperationInProgress
from remoteappmanager.docker.image import Image
from remoteappmanager.tests import utils
from remoteappmanager.tests.mocking.virtual.docker_client import (
    create_docker_client)


class TestContainerManager(AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.manager = ContainerManager({})
        self.mock_docker_client = create_docker_client()
        self.manager.docker_client._sync_client = self.mock_docker_client

    def test_instantiation(self):
        self.assertIsNotNone(self.manager.docker_client)

    @gen_test
    def test_start_stop(self):
        mock_client = self.mock_docker_client

        result = yield self.manager.start_container(
            "username",
            'image_id1',
            "new_mapping_id",
            "/base/url",
            None,
            None)
        self.assertTrue(mock_client.start.called)
        self.assertTrue(mock_client.create_container.called)

        runinfo_labels = mock_client.create_container.call_args[1]["labels"]

        self.assertEqual(runinfo_labels[SIMPHONY_NS_RUNINFO.user], "username")
        self.assertIn(SIMPHONY_NS_RUNINFO.url_id, runinfo_labels)
        self.assertEqual(runinfo_labels[SIMPHONY_NS_RUNINFO.mapping_id],
                         "new_mapping_id")

        self.assertIsInstance(result, Container)
        self.assertFalse(mock_client.stop.called)
        self.assertFalse(mock_client.remove_container.called)

        yield self.manager.stop_and_remove_container(result.docker_id)

        self.assertTrue(mock_client.stop.called)
        self.assertTrue(mock_client.remove_container.called)

    @gen_test
    def test_containers_from_mapping_id(self):
        ''' Test containers_for_mapping_id returns a list of Container '''
        result = yield self.manager.containers_from_mapping_id("user_name",
                                                               "mapping_id")
        expected = Container(docker_id='container_id1',
                             mapping_id="mapping_id",
                             name='/remoteexec-username-mapping_5Fid',
                             image_name='image_name1',  # noqa
                             user="user_name",
                             image_id='image_id1',
                             ip='127.0.0.1',
                             port=666,
                             url_id='url_id',
                             urlpath="/user/username/containers/url_id")

        self.assertEqual(len(result), 1)
        utils.assert_containers_equal(self, result[0], expected)

    @gen_test
    def test_containers_from_url_id(self):
        ''' Test containers_for_mapping_id returns a list of Container '''
        result = yield self.manager.container_from_url_id("url_id")
        expected = Container(docker_id='container_id1',
                             mapping_id="mapping_id",
                             name='/remoteexec-username-mapping_5Fid',
                             image_name='image_name1',  # noqa
                             user="user_name",
                             image_id='image_id1',
                             ip='127.0.0.1',
                             port=666,
                             url_id='url_id',
                             urlpath="/user/username/containers/url_id",
                             )

        utils.assert_containers_equal(self, result, expected)

    @gen_test
    def test_containers_from_url_id_exceptions(self):
        ''' Test containers_for_mapping_id returns a list of Container '''
        docker_client = self.mock_docker_client
        docker_client.port = mock.Mock(side_effect=Exception("Boom!"))

        result = yield self.manager.container_from_url_id("url_id")
        self.assertEqual(result, None)

        # Making it so that no valid dictionary is returned.
        docker_client.port = mock.Mock(return_value=1234)
        self.mock_docker_client = docker_client
        self.manager.docker_client._sync_client = docker_client

        result = yield self.manager.container_from_url_id("url_id")
        self.assertEqual(result, None)

    @gen_test
    def test_running_containers(self):
        result = yield self.manager.running_containers()
        self.assertEqual(len(result), 1)

    @gen_test
    def test_race_condition_spawning(self):
        # Start the operations, and retrieve the future.
        # they will stop at the first yield and not go further until
        # we yield them
        f1 = self.manager.start_container("username",
                                          "image_id1",
                                          "mapping_id",
                                          "/foo/bar",
                                          None,
                                          )

        f2 = self.manager.start_container("username",
                                          "image_id1",
                                          "mapping_id",
                                          "/foo/baz",
                                          None,
                                          )

        # If these yielding raise a KeyError, it is because the second
        # one tries to remove the same key from the list, but it has been
        # already removed by the first one. Race condition.
        yield f1

        with self.assertRaises(OperationInProgress):
            yield f2

        self.assertEqual(self.mock_docker_client.start.call_count, 1)

    @gen_test
    def test_race_condition_stopping(self):
        f1 = self.manager.stop_and_remove_container("12345")
        f2 = self.manager.stop_and_remove_container("12345")

        yield f1

        with self.assertRaises(OperationInProgress):
            yield f2

        self.assertEqual(self.mock_docker_client.stop.call_count, 1)

    @gen_test
    def test_start_already_present_container(self):
        mock_client = self.mock_docker_client

        result = yield self.manager.start_container(
            "username",
            "image_name1",
            "mapping_id",
            "/base/url",
            None,
            None)
        self.assertTrue(mock_client.start.called)
        self.assertIsInstance(result, Container)

        # Stop should have been called and the container removed
        self.assertTrue(mock_client.stop.called)
        self.assertTrue(mock_client.remove_container.called)

    @gen_test
    def test_image(self):
        image = yield self.manager.image('image_name1')
        self.assertIsInstance(image, Image)
        self.assertEqual(image.description,
                         'Ubuntu machine with mayavi preinstalled')
        self.assertEqual(image.icon_128, "")
        self.assertEqual(image.ui_name, "Mayavi 4.4.4")
        self.assertEqual(image.docker_id, 'image_id1')

        image = yield self.manager.image("whatev")
        self.assertIsNone(image)

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

        yield self.manager.start_container("username",
                                           "image_id1",
                                           "mapping_id",
                                           "/foo/bar",
                                           volumes,
                                           )

        # Call args and keyword args that create_container receives
        docker_client = self.manager.docker_client
        args = docker_client._sync_client.create_container.call_args
        actual_volume_targets = args[1]['volumes']

        # Invalid volume paths should have been filtered away
        self.assertNotIn('/target_vol1', actual_volume_targets)
        self.assertNotIn('/target_vol2', actual_volume_targets)

        # The current directory is valid, should stay
        self.assertIn('/target_vol3', actual_volume_targets)

    @gen_test
    def test_start_container_exception_cleanup(self):
        self.assertFalse(self.mock_docker_client.stop.called)
        self.assertFalse(self.mock_docker_client.remove_container.called)

        def raiser(*args, **kwargs):
            raise Exception("Boom!")

        self.manager.docker_client.start = mock.Mock(side_effect=raiser)

        with self.assertRaisesRegex(Exception, 'Boom!'):
            yield self.manager.start_container("username",
                                               "image_id1",
                                               "mapping_id",
                                               "/base/url",
                                               None,
                                               None)

        self.assertTrue(self.mock_docker_client.stop.called)
        self.assertTrue(self.mock_docker_client.remove_container.called)

    @gen_test
    def test_start_container_exception_cleanup_2(self):
        # Same test as above, but checks after the start (at ip and port)
        self.assertFalse(self.mock_docker_client.stop.called)
        self.assertFalse(self.mock_docker_client.remove_container.called)

        def raiser(*args, **kwargs):
            raise Exception("Boom!")

        self.manager.docker_client.port = mock.Mock(side_effect=raiser)

        with self.assertRaisesRegex(Exception, 'Boom!'):
            yield self.manager.start_container("username",
                                               "image_id1",
                                               "mapping_id",
                                               "/base/url",
                                               None,
                                               None)

        self.assertTrue(self.mock_docker_client.stop.called)
        self.assertTrue(self.mock_docker_client.remove_container.called)

    @gen_test
    def test_start_container_with_environment(self):
        mock_client = self.mock_docker_client

        environment = {
            "FOO": "bar"
        }

        yield self.manager.start_container(
            "username",
            "image_name1",
            "mapping_id",
            "/base/url",
            None,
            environment)

        self.assertEqual(
            mock_client.create_container.call_args[1]["environment"]["FOO"],
            "bar")
