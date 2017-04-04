from unittest import TestCase

from remoteappmanager.docker.container import Container
from remoteappmanager.docker.docker_labels import (
    SIMPHONY_NS, SIMPHONY_NS_RUNINFO)
from remoteappmanager.tests.mocking.virtual.docker_client import \
    VirtualDockerClient
from remoteappmanager.tests.utils import assert_containers_equal


class TestContainer(TestCase):
    def setUp(self):
        self.good_container_dict = {
            'Command': '/startup.sh',
            'Created': 1466756760,
            'HostConfig': {'NetworkMode': 'default'},
            'Id': '248e45e717cd740ae763a1c565',
            'Image': 'empty-ubuntu:latest',
            'ImageID': 'sha256:f4610c7580b8f0a9a25086b6287d0069fb8a',
            'Labels': {SIMPHONY_NS.ui_name: 'Empty Ubuntu',
                       SIMPHONY_NS_RUNINFO.user: 'user',
                       SIMPHONY_NS_RUNINFO.url_id: "8e2fe66d5de74db9bbab50c0d2f92b33",  # noqa
                       SIMPHONY_NS_RUNINFO.realm: "myrealm",
                       SIMPHONY_NS_RUNINFO.mapping_id: "mapping_id",
                       SIMPHONY_NS_RUNINFO.urlpath: "/user/username/containers/8e2fe66d5de74db9bbab50c0d2f92b33"},  # noqa
            'Names': ['/myrealm-user-empty-ubuntu_3Alatest'],
            'Ports': [{'IP': '0.0.0.0',
                       'PrivatePort': 8888,
                       'PublicPort': 32823,
                       'Type': 'tcp'}],
            'State': 'running',
            'Status': 'Up 56 minutes'}

    def test_host_url(self):
        container = Container(
            ip="123.45.67.89",
            port=31337
        )

        self.assertEqual(container.host_url, "http://123.45.67.89:31337")

    def test_from_docker_dict_with_public_port(self):
        """Test convertion from "docker ps" to Container with public port"""
        # With public port
        container_dict = self.good_container_dict

        # Container with public port
        actual = Container.from_docker_dict(container_dict)
        expected = Container(
            docker_id='248e45e717cd740ae763a1c565',
            name='/myrealm-user-empty-ubuntu_3Alatest',
            image_name='empty-ubuntu:latest',
            image_id='sha256:f4610c7580b8f0a9a25086b6287d0069fb8a',
            user="user",
            ip='0.0.0.0',
            port=32823,
            mapping_id="mapping_id",
            url_id="8e2fe66d5de74db9bbab50c0d2f92b33",
            urlpath="/user/username/containers/8e2fe66d5de74db9bbab50c0d2f92b33",  # noqa
            realm="myrealm"
        )

        assert_containers_equal(self, actual, expected)

    def test_failure_for_incorrect_urlpath(self):
        labels = self.good_container_dict["Labels"]
        labels[SIMPHONY_NS_RUNINFO.urlpath] = (
            labels[SIMPHONY_NS_RUNINFO.urlpath] + '/')

        with self.assertRaises(ValueError):
            Container.from_docker_dict(self.good_container_dict)

    def test_no_realm(self):
        labels = self.good_container_dict["Labels"]
        labels[SIMPHONY_NS_RUNINFO.realm] = ""

        container = Container.from_docker_dict(self.good_container_dict)

        self.assertEqual(container.realm, "")

    def test_from_docker_dict_without_public_port(self):
        container_dict = self.good_container_dict
        del container_dict["Ports"][0]["PublicPort"]

        # Container without public port
        actual = Container.from_docker_dict(container_dict)
        expected = Container(
            docker_id='248e45e717cd740ae763a1c565',
            name='/myrealm-user-empty-ubuntu_3Alatest',
            image_name='empty-ubuntu:latest',
            image_id='sha256:f4610c7580b8f0a9a25086b6287d0069fb8a',
            user="user",
            ip='0.0.0.0',
            port=80,
            url_id="8e2fe66d5de74db9bbab50c0d2f92b33"
        )
        assert_containers_equal(self, actual, expected)

    def test_from_docker_dict_inspect_container(self):
        client = VirtualDockerClient.with_containers()
        actual = Container.from_docker_dict(
            client.inspect_container('d2b56bffb5655cb7668b685b80116041a20ee8662ebfa5b5cb68cfc423d9dc30'))  # noqa

        expected = Container(
            docker_id='d2b56bffb5655cb7668b685b80116041a20ee8662ebfa5b5cb68cfc423d9dc30',  # noqa
            name='/myrealm-username-mapping_5Fid',
            image_name='image_name1',
            image_id='image_id1',
            user="username",
            ip='0.0.0.0',
            port=666,
            url_id="url_id",
            mapping_id="mapping_id",
            realm="myrealm",
            urlpath="/user/username/containers/8e2fe66d5de74db9bbab50c0d2f92b33"  # noqa
        )

        assert_containers_equal(self, actual, expected)

    def test_multiple_ports_data(self):
        docker_dict = {'Id': 'container_id1',
                       'Config': {
                           'Labels': {
                               'eu.simphony-project.docker.ui_name': 'Mayavi 4.4.4',  # noqa
                               'eu.simphony-project.docker.env.x11-depth': '',
                               'eu.simphony-project.docker.type': 'vncapp',
                               'eu.simphony-project.docker.env.x11-height': '',
                               'eu.simphony-project.docker.env.x11-width': '',
                               'eu.simphony-project.docker.description':
                                   'Ubuntu machine with mayavi preinstalled'},
                           'Image': 'image_name1'
                       },
                       'NetworkSettings': {
                           'Ports': {
                               '8889/tcp': [
                                   {'HostPort': '667',
                                    'HostIp': '0.0.0.0'}
                               ],
                               '8888/tcp': [
                                   {'HostPort': '666', 'HostIp': '0.0.0.0'}
                               ]
                           }
                       },
                       'Name': '/container_name1',
                       'State': 'running',
                       'Image': 'image_id1'
                       }

        docker_dict["NetworkSettings"]["Ports"] = {
            '8888/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '666'}],
            '8889/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '667'}]
        }
        with self.assertRaises(ValueError):
            Container.from_docker_dict(docker_dict)

        docker_dict["NetworkSettings"]["Ports"] = {
            '8888/tcp': [
                {'HostIp': '0.0.0.0', 'HostPort': '32782'},
                {'HostIp': '0.0.0.0', 'HostPort': '32783'}
            ]
        }
        with self.assertRaises(ValueError):
            Container.from_docker_dict(docker_dict)

        docker_dict = {
            'Labels': {
                'eu.simphony-project.docker.runinfo.user': 'user_name',
                'eu.simphony-project.docker.env.x11-depth': '',
                'eu.simphony-project.docker.runinfo.mapping_id': 'mapping_id',
                'eu.simphony-project.docker.env.x11-height': '',
                'eu.simphony-project.docker.ui_name': 'Mayavi 4.4.4',
                'eu.simphony-project.docker.runinfo.urlpath': '/user/username/containers/url_id',  # noqa
                'eu.simphony-project.docker.type': 'vncapp',
                'eu.simphony-project.docker.runinfo.realm': 'myrealm',
                'eu.simphony-project.docker.description': 'Ubuntu machine with mayavi preinstalled',  # noqa
                'eu.simphony-project.docker.env.x11-width': '',
                'eu.simphony-project.docker.runinfo.url_id': 'url_id'
            },
            'Names': ['/myrealm-username-mapping_5Fid'],
            'Ports': [{'Type': 'tcp', 'IP': '0.0.0.0', 'PublicPort': 666, 'PrivatePort': 8888}],  # noqa
            'State': 'running',
            'Command': '/sbin/init -D',
            'Image': 'image_name1',
            'Id': 'container_id1', 'ImageID': 'image_id1'
        }

        docker_dict["Ports"] = [
             {
                'IP': '0.0.0.0',
                'PublicIP': 34567,
                'PrivatePort': 22,
                'Type': 'tcp'
             },
             {
                'IP': '0.0.0.0',
                'PublicIP': 34562,
                'PrivatePort': 21,
                'Type': 'tcp'
             }
        ]
        with self.assertRaises(ValueError):
            Container.from_docker_dict(docker_dict)
