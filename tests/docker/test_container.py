from unittest import TestCase

from remoteappmanager.docker.container import Container
from tests.utils import assert_containers_equal


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

    def test_from_docker_dict_with_public_port(self):
        '''Test convertion from "docker ps" to Container with public port'''
        # With public port
        container_dict = {
            'Command': '/startup.sh',
            'Created': 1466756760,
            'HostConfig': {'NetworkMode': 'default'},
            'Id': '248e45e717cd740ae763a1c565',
            'Image': 'empty-ubuntu:latest',
            'ImageID': 'sha256:f4610c7580b8f0a9a25086b6287d0069fb8a',
            'Labels': {'eu.simphony-project.docker.ui_name': 'Empty Ubuntu',
                       'eu.simphony-project.docker.user': 'user'},
            'Names': ['/remoteexec-user-empty-ubuntu_3Alatest'],
            'Ports': [{'IP': '0.0.0.0',
                       'PrivatePort': 8888,
                       'PublicPort': 32823,
                       'Type': 'tcp'}],
            'State': 'running',
            'Status': 'Up 56 minutes'}

        # Container with public port
        actual = Container.from_docker_dict(container_dict)
        expected = Container(
            docker_id='248e45e717cd740ae763a1c565',
            name='/remoteexec-user-empty-ubuntu_3Alatest',
            image_name='empty-ubuntu:latest',
            image_id='sha256:f4610c7580b8f0a9a25086b6287d0069fb8a',
            ip='0.0.0.0', port=32823)

        assert_containers_equal(self, actual, expected)

    def test_from_docker_dict_without_public_port(self):
        '''Test convertion from "docker ps" to Container with public port'''
        # With public port
        container_dict = {
            'Command': '/startup.sh',
            'Created': 1466756760,
            'HostConfig': {'NetworkMode': 'default'},
            'Id': '812c765d0549be0ab831ae8348',
            'Image': 'novnc-ubuntu:latest',
            'ImageID': 'sha256:f4610c75d3c0dfa25d3c0dfa25d3c0dfa2',
            'Labels': {'eu.simphony-project.docker.ui_name': 'Empty Ubuntu',
                       'eu.simphony-project.docker.user': 'user'},
            'Names': ['/remoteexec-user-empty-ubuntu_3Alatest'],
            'Ports': [{'IP': '0.0.0.0',
                       'PrivatePort': 8888,
                       'Type': 'tcp'}],
            'State': 'running',
            'Status': 'Up 56 minutes'}

        # Container without public port
        actual = Container.from_docker_dict(container_dict)
        expected = Container(
            docker_id='812c765d0549be0ab831ae8348',
            name='/remoteexec-user-empty-ubuntu_3Alatest',
            image_name='novnc-ubuntu:latest',
            image_id='sha256:f4610c75d3c0dfa25d3c0dfa25d3c0dfa2',
            ip='0.0.0.0', port=None)

        assert_containers_equal(self, actual, expected)
