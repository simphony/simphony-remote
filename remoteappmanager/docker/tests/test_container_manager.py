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
    VirtualDockerClient)


class TestContainerManager(AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.manager = ContainerManager(docker_config={}, realm="myrealm")
        self.mock_docker_client = VirtualDockerClient.with_containers()
        self.manager._docker_client._sync_client = self.mock_docker_client

    def test_instantiation(self):
        self.assertIsNotNone(self.manager._docker_client)

    @gen_test
    def test_start_stop(self):
        mock_client = self.mock_docker_client
        with mock.patch.object(mock_client, "start",
                               wraps=mock_client.start), \
            mock.patch.object(mock_client, "stop",
                              wraps=mock_client.stop), \
            mock.patch.object(mock_client, "create_container",
                              wraps=mock_client.create_container), \
            mock.patch.object(mock_client, "remove_container",
                              wraps=mock_client.remove_container):

            result = yield self.manager.start_container(
                "johndoe",
                'simphonyproject/simphony-mayavi:0.6.0',
                "63dce9335bca49798bbb93146ad07c66",
                "/user/johndoe/containers/cbeb652678244ed1aa5f68735abb4868",
                None,
                None)

            self.assertTrue(mock_client.start.called)
            self.assertTrue(mock_client.create_container.called)

            runinfo_labels = mock_client.create_container.call_args[1][
                "labels"]

            self.assertEqual(runinfo_labels[SIMPHONY_NS_RUNINFO.user],
                             "johndoe")
            self.assertEqual(runinfo_labels[SIMPHONY_NS_RUNINFO.realm],
                             "myrealm")
            self.assertIn(SIMPHONY_NS_RUNINFO.url_id, runinfo_labels)
            self.assertEqual(runinfo_labels[SIMPHONY_NS_RUNINFO.mapping_id],
                             "63dce9335bca49798bbb93146ad07c66")

            self.assertIsInstance(result, Container)
            self.assertFalse(mock_client.stop.called)
            self.assertFalse(mock_client.remove_container.called)

            yield self.manager.stop_and_remove_container(result.docker_id)

            self.assertTrue(mock_client.stop.called)
            self.assertTrue(mock_client.remove_container.called)

    @gen_test
    def test_find_from_mapping_id(self):
        """ Test containers_for_mapping_id returns a list of Container """
        result = yield self.manager.find_containers(
            user_name="johndoe",
            mapping_id="5b34ce60d95742fa828cdced12b4c342")

        expected = Container(docker_id='d2b56bffb5655cb7668b685b80116041a20ee8662ebfa5b5cb68cfc423d9dc30',  # noqa
                             mapping_id="5b34ce60d95742fa828cdced12b4c342",
                             name="/myrealm-johndoe-5b34ce60d95742fa828cdced12b4c342-ascvbefsda",  # noqa
                             image_name='simphonyproject/simphony-mayavi:0.6.0',  # noqa
                             user="johndoe",
                             image_id="sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824", # noqa
                             ip='127.0.0.1',
                             port=666,
                             url_id='20dcb84cdbea4b1899447246789093d0',
                             realm="myrealm",
                             urlpath="/user/johndoe/containers/20dcb84cdbea4b1899447246789093d0"  # noqa
                             )

        self.assertEqual(len(result), 1)
        utils.assert_containers_equal(self, result[0], expected)

    @gen_test
    def test_find_from_url_id(self):
        """ Test containers_for_mapping_id returns a list of Container """
        result = yield self.manager.find_container(
            url_id="20dcb84cdbea4b1899447246789093d0")

        expected = Container(docker_id='d2b56bffb5655cb7668b685b80116041a20ee8662ebfa5b5cb68cfc423d9dc30',  # noqa
                             mapping_id="5b34ce60d95742fa828cdced12b4c342",
                             name="/myrealm-johndoe-5b34ce60d95742fa828cdced12b4c342-ascvbefsda",  # noqa
                             image_name='simphonyproject/simphony-mayavi:0.6.0',  # noqa
                             user="johndoe",
                             image_id="sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824", # noqa
                             ip='127.0.0.1',
                             port=666,
                             url_id='20dcb84cdbea4b1899447246789093d0',
                             realm="myrealm",
                             urlpath="/user/johndoe/containers/20dcb84cdbea4b1899447246789093d0"  # noqa
                             )

        utils.assert_containers_equal(self, result, expected)

    @gen_test
    def test_find_from_url_id_exceptions(self):
        """ Test containers_for_mapping_id returns a list of Container """
        docker_client = self.mock_docker_client
        docker_client.port = mock.Mock(side_effect=Exception("Boom!"))

        result = yield self.manager.find_container(url_id="url_id")
        self.assertEqual(result, None)

        # Making it so that no valid dictionary is returned.
        docker_client.port = mock.Mock(return_value=1234)
        self.mock_docker_client = docker_client
        self.manager._docker_client._sync_client = docker_client

        result = yield self.manager.find_container(url_id="url_id")
        self.assertEqual(result, None)

    @gen_test
    def test_find_containers(self):
        result = yield self.manager.find_containers()
        self.assertEqual(len(result), 1)

    @gen_test
    def test_race_condition_spawning(self):
        # Start the operations, and retrieve the future.
        # they will stop at the first yield and not go further until
        # we yield them
        with mock.patch.object(self.mock_docker_client, "start",
                               wraps=self.mock_docker_client.start):
            f1 = self.manager.start_container("johndoe",
                                              "simphonyproject/simphony-mayavi:0.6.0",  # noqa
                                              "76cd29a4d61f4ddc95fa633347934807",  # noqa
                                              "/user/johndoe/containers/4b9a34d803c74013939d8df05eef9262",  # noqa
                                              None,
                                              )

            f2 = self.manager.start_container("johndoe",
                                              "simphonyproject/simphony-mayavi:0.6.0",  # noqa
                                              "76cd29a4d61f4ddc95fa633347934807",  # noqa
                                              "/user/johndoe/containers/a2612a5a12074ce99ece1c2888fe34c0",  # noqa
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
        docker_client = self.mock_docker_client

        with mock.patch.object(docker_client, "stop",
                               wraps=docker_client.stop):

            f1 = self.manager.stop_and_remove_container("d2b56bffb5655cb7668b685b80116041a20ee8662ebfa5b5cb68cfc423d9dc30")  # noqa
            f2 = self.manager.stop_and_remove_container("d2b56bffb5655cb7668b685b80116041a20ee8662ebfa5b5cb68cfc423d9dc30")  # noqa

            yield f1

            with self.assertRaises(OperationInProgress):
                yield f2

            self.assertEqual(self.mock_docker_client.stop.call_count, 1)

    @gen_test
    def test_start_already_present_container(self):
        mock_client = self.mock_docker_client

        with mock.patch.object(mock_client, "start",
                               wraps=mock_client.start), \
            mock.patch.object(mock_client, "stop",
                              wraps=mock_client.stop), \
            mock.patch.object(mock_client, "remove_container",
                              wraps=mock_client.remove_container):

            result = yield self.manager.start_container(
                "johndoe",
                "simphonyproject/simphony-mayavi:0.6.0",
                "5b34ce60d95742fa828cdced12b4c342",
                "/users/johndoe/containers/random_value",
                None,
                None)
            self.assertTrue(mock_client.start.called)
            self.assertIsInstance(result, Container)

            # Stop should have been called and the container removed
            self.assertTrue(mock_client.stop.called)
            self.assertTrue(mock_client.remove_container.called)

    @gen_test
    def test_image(self):
        image = yield self.manager.image('simphonyproject/simphony-mayavi:0.6.0')  # noqa
        self.assertIsInstance(image, Image)
        self.assertEqual(image.description,
                         'Ubuntu machine with mayavi preinstalled')
        self.assertEqual(image.icon_128, "")
        self.assertEqual(image.ui_name, "Mayavi 4.4.4")
        self.assertEqual(image.docker_id, "sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824")  # noqa

        image = yield self.manager.image("whatev")
        self.assertIsNone(image)

    @gen_test
    def test_start_container_with_nonexisting_volume_source(self):
        # These volume sources are invalid
        docker_client = self.manager._docker_client._sync_client
        with mock.patch.object(docker_client, "create_container",
                               wraps=docker_client.create_container):
            volumes = {'~no_way_this_be_valid': {'bind': '/target_vol1',
                                                 'mode': 'ro'},
                       '/no_way_this_be_valid': {'bind': '/target_vol2',
                                                 'mode': 'ro'}}

            # This volume source is valid
            good_path = os.path.abspath('.')
            volumes[good_path] = {'bind': '/target_vol3',
                                  'mode': 'ro'}

            yield self.manager.start_container("johndoe",
                                               "simphonyproject/simphony-mayavi:0.6.0",  # noqa
                                               "5b34ce60d95742fa828cdced12b4c342",
                                               "/foo/bar",
                                               volumes,
                                               )

            # Call args and keyword args that create_container receives
            args = docker_client.create_container.call_args
            actual_volume_targets = args[1]['volumes']

            # Invalid volume paths should have been filtered away
            self.assertNotIn('/target_vol1', actual_volume_targets)
            self.assertNotIn('/target_vol2', actual_volume_targets)

            # The current directory is valid, should stay
            self.assertIn('/target_vol3', actual_volume_targets)

    @gen_test
    def test_start_container_exception_cleanup(self):
        docker_client = self.mock_docker_client

        def raiser(*args, **kwargs):
            raise Exception("Boom!")

        with mock.patch.object(docker_client, "stop",
                               wraps=docker_client.stop), \
            mock.patch.object(docker_client, "remove_container",
                              wraps=docker_client.remove_container), \
            mock.patch.object(docker_client, "start",
                              side_effect=raiser):

            self.assertFalse(self.mock_docker_client.stop.called)
            self.assertFalse(self.mock_docker_client.remove_container.called)

            with self.assertRaisesRegex(Exception, 'Boom!'):
                yield self.manager.start_container("johndoe",
                                                   "simphonyproject/simphony-mayavi:0.6.0",  # noqa
                                                   "5b34ce60d95742fa828cdced12b4c342",  # noqa
                                                   "/users/johndoe/containers/4273750ddce3454283a5b1817526260b/",  # noqa
                                                   None,
                                                   None)

            self.assertTrue(docker_client.stop.called)
            self.assertTrue(docker_client.remove_container.called)

    @gen_test
    def test_start_container_exception_cleanup_2(self):
        # Same test as above, but checks after the start (at ip and port)
        docker_client = self.mock_docker_client

        def raiser(*args, **kwargs):
            raise Exception("Boom!")

        with mock.patch.object(docker_client, "stop",
                               wraps=docker_client.stop), \
            mock.patch.object(docker_client, "remove_container",
                              wraps=docker_client.remove_container), \
            mock.patch.object(docker_client, "port",
                              side_effect=raiser):

            self.manager._docker_client.port = mock.Mock(side_effect=raiser)

            with self.assertRaisesRegex(Exception, 'Boom!'):
                yield self.manager.start_container("johndoe",
                                                   "simphonyproject/simphony-mayavi:0.6.0",  # noqa
                                                   "4273750ddce3454283a5b1817526260b",  # noqa
                                                   "/users/johndoe/containers/3b83f81f2e4544e6aa1493b50202f8eb",  # noqa
                                                   None,
                                                   None)

            self.assertTrue(self.mock_docker_client.stop.called)
            self.assertTrue(self.mock_docker_client.remove_container.called)

    @gen_test
    def test_start_container_with_environment(self):
        mock_client = self.mock_docker_client
        with mock.patch.object(mock_client, "create_container",
                               wraps=mock_client.create_container):

            environment = {
                "FOO": "bar"
            }

            yield self.manager.start_container(
                "johndoe",
                "simphonyproject/simphony-mayavi:0.6.0",
                "4273750ddce3454283a5b1817526260b",
                "/users/johndoe/containers/3b83f81f2e4544e6aa1493b50202f8eb",
                None,
                environment)

            self.assertEqual(
                mock_client.create_container.call_args[1][
                    "environment"]["FOO"],
                "bar")

    @gen_test
    def test_different_realm(self):
        manager = ContainerManager(docker_config={},
                                   realm="anotherrealm")
        manager._docker_client._sync_client = \
            VirtualDockerClient.with_containers()

        result = yield manager.find_container(
            user_name="johndoe", mapping_id="5b34ce60d95742fa828cdced12b4c342")
        self.assertIsNone(result)

        result = yield manager.find_containers()
        self.assertEqual(result, [])

    @gen_test
    def test_not_stopping_if_different_realm(self):
        self.mock_docker_client.stop = mock.Mock()
        self.mock_docker_client.remove_container = mock.Mock()
        manager = ContainerManager(docker_config={},
                                   realm="anotherrealm")
        yield manager.stop_and_remove_container("d2b56bffb5655cb7668b685b80116041a20ee8662ebfa5b5cb68cfc423d9dc30")  # noqa

        self.assertFalse(self.mock_docker_client.stop.called)
        self.assertFalse(self.mock_docker_client.remove_container.called)
