import json
import uuid
import requests
from collections import namedtuple

import docker

from remoteappmanager.docker.docker_labels import (
    SIMPHONY_NS,
    SIMPHONY_NS_ENV,
    SIMPHONY_NS_RUNINFO)

# internal, convenience classes. Do not export (risks name collisions with
# container manager similarly named entities.

_Image = namedtuple("Image",
                    field_names="id name labels exposed_ports")
_Container = namedtuple("Container",
                        field_names="id name image labels ports state")


class VirtualDockerClient(object):
    """A virtual docker client that behaves like the real thing
    but does nothing on docker. It provides the same interface as dockerpy
    Client.
    """

    def __init__(self):
        # This entry contains the images that can be installed.
        # It simulates the hub docker retrieval.
        self._available_images = self._init_available_images()

        # This contains the images that are currently installed.
        self._images = []

        # This one contains the containers that are currently present
        self._containers = []

    @classmethod
    def with_containers(cls):
        """
        Alternative constructor.
        When created, it provides a predefined set of available images.
        """
        self = cls()

        self._images = self._available_images[:]
        self._containers = [
            _Container(
                id="223c6fc3c5054b7e916ab000ae302df3",
                name="realm-johndoe-5b34ce60d95742fa828cdced12b4c342",
                image="simphonyproject/simphony-mayavi",
                labels={
                    SIMPHONY_NS_RUNINFO.user: 'johndoe',
                    SIMPHONY_NS_RUNINFO.mapping_id: '5b34ce60d95742fa828cdced12b4c342',  # noqa
                    SIMPHONY_NS_RUNINFO.url_id: '20dcb84cdbea4b1899447246789093d0',  # noqa
                    SIMPHONY_NS_RUNINFO.realm: 'realm',
                    SIMPHONY_NS_RUNINFO.urlpath: '/user/username/containers/20dcb84cdbea4b1899447246789093d0'  # noqa
                },
                ports=[{
                    "IP": "0.0.0.0",
                    "PublicPort": 666,
                    "PrivatePort": 8888,
                    "Type": "tcp",
                }],
                state="running",
            ),
            _Container(
                id="d04eaa6e2c36419cb25b316231a201c0",
                name="realm-johndoe-6d24a0746a4e409c9b9078b158b8c484",
                image="simphonyproject/simphony-mayavi",
                labels={
                    SIMPHONY_NS_RUNINFO.user: 'johndoe',
                    SIMPHONY_NS_RUNINFO.mapping_id: 'db3890933e4843f092e954fc5e0caf9e',  # noqa
                    SIMPHONY_NS_RUNINFO.url_id: '90d581268df8428aa91d56a62d83b163',  # noqa
                    SIMPHONY_NS_RUNINFO.realm: 'realm',
                    SIMPHONY_NS_RUNINFO.urlpath: '/user/username/containers/90d581268df8428aa91d56a62d83b163'  # noqa
                },
                ports=[{
                    "PrivatePort": 8889,
                    "Type": "tcp",
                }],
                state="exited",
            ),
            _Container(
                id="51e69f95a0d04294a2956c35e2894661",
                name="realm-johndoe-27d17e78297441fdbe43ee6b8c148a17",
                image="simphonyproject/simphony-mayavi",
                labels={},
                ports=[{
                    "IP": "0.0.0.0",
                    "PublicPort": 666,
                    "PrivatePort": 8888,
                    "Type": "tcp",
                }],
                state={'Paused': False,
                       'Running': False,
                       'Error': '',
                       'Pid': 0,
                       'FinishedAt': '2016-06-22T09:15:35.574996772Z',
                       'StartedAt': '2016-06-22T09:15:02.196670642Z',
                       'Restarting': False,
                       'Status': 'exited',
                       'Dead': False,
                       'OOMKilled': False,
                       'ExitCode': 0},
            ),
        ]

        return self

    # API of the dockerpy Docker client.

    def inspect_image(self, image_name_or_id):
        image = self._find_image(image_name_or_id)

        return {'Config': {'Cmd': None,
                           'Domainname': '',
                           'Entrypoint': ['/startup.sh'],
                           'ExposedPorts': {'8888/tcp': {}},
                           'Labels': image.labels},
                'Id': image.id,
                'RepoTags': [image.name]}

    def images(self):
        return [{'Created': '2 days ago',
                 'Id': image.id,
                 'Labels': image.labels,
                 'RepoTags': [image.name]}
                for image in self._images]

    def create_container(self, *args, **kwargs):
        id = self._new_id()
        self._containers.append(
            _Container(
                id=id,
                name=kwargs["name"],
                image=kwargs["image"],
                labels=kwargs.get("labels", {}),
                ports=[{
                    "IP": "0.0.0.0",
                    "PublicPort": 666,
                    "PrivatePort": 8888,
                    "Type": "tcp",
                }],
                state="running",
            )
        )

        return {"Id": id}

    def containers(self, *args, **kwargs):
        results = []

        for container in self._containers:
            image = self._find_image(container.image)
            if container.state != 'running' and not kwargs.get('all', False):
                continue

            all_labels = image.labels.copy()
            all_labels.update(container.labels)

            # Apply filters for labels
            if 'filters' in kwargs and 'label' in kwargs['filters']:
                label_filters = kwargs['filters']['label']

                if not isinstance(label_filters, (list, tuple)):
                    label_filters = [label_filters]

                label_filters = (label.split('=') for label in label_filters)
                if any(label_name not in all_labels or
                       all_labels[label_name] != label_value
                       for label_name, label_value in label_filters):
                    continue

            results.append(
                {'Command': '/sbin/init -D',
                 'Id': container.id,
                 'Image': image.name,
                 'ImageID': image.id,
                 'Labels': all_labels,
                 'Names': ['/'+container.name],
                 'Ports': container.ports,
                 'State': container.state})

        return results

    def inspect_container(self, container_name_or_id):
        container = self._find_container(container_name_or_id)
        image = self._find_image(container.image)
        labels = container.labels

        all_labels = image.labels.copy()
        all_labels.update(labels)

        network_settings = {}

        if container.ports:
            network_settings['Ports'] = {}

            for port_settings in container.ports:
                target = '{}/{}'.format(port_settings.get('PrivatePort', ''),
                                        port_settings.get('Type', 'tcp'))
                host_ip = port_settings.get('IP', '')
                host_port = port_settings.get('PublicPort', '')
                network_settings['Ports'][target] = [
                    {'HostIp': str(host_ip),
                     'HostPort': str(host_port)}]

        return {'State': container.state,
                'Name': '/'+container.name,
                'Image': image.id,
                'Config': {
                    'Image': image.name,
                    'Labels': all_labels},
                'Id': container.id,
                'NetworkSettings': network_settings
                }

    def port(self, container_name_or_id, private_port):
        container = self._find_container(container_name_or_id)

        if container.ports:
            host_ip = container.ports[0].get('IP', '')
            host_port = container.ports[0].get('PublicPort', '')
        else:
            host_ip = host_port = ''

        return [{'HostIp': host_ip,
                 'HostPort': host_port}]

    def start(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        pass

    def remove_container(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        return {"ID": "something"}

    def create_host_config(self, **kwargs):
        return {}

    # Additional API for convenience's sake

    def add_container_from_raw_info(self, id, name,
                                    image, labels, ports, state):
        self._containers.append(
            _Container(id, name, image, labels, ports, state)
        )

    def _find_image(self, image_name_or_id):
        image_ids = {image.id: image for image in self._images}
        image_names = {image.name: image for image in self._images}

        image = image_ids.get(image_name_or_id)
        if image is None:
            image = image_names.get(image_name_or_id)

        if image is None:
            raise docker.errors.NotFound(
                'No such image: {}'.format(image_name_or_id),
                response=self._docker_response(404))

        return image

    def _find_container(self, container_name_or_id):
        container_ids = {container.id: container
                         for container in self._containers}
        container_names = {container.name: container
                           for container in self._containers}

        container = container_ids.get(container_name_or_id)
        if container is None:
            container = container_names.get(container_name_or_id)

        if container is None:
            raise docker.errors.NotFound(
                'Container {} not found'.format(container_name_or_id),
                response=self._docker_response(404))

        return container

    def _docker_response(self, status_code=200, content='',
                         headers=None, reason=None,
                         request=None):
        res = requests.Response()
        res.status_code = status_code
        content = json.dumps(content).encode('ascii')
        res._content = content
        res.headers = requests.structures.CaseInsensitiveDict(headers or {})
        res.reason = reason
        res.request = request
        return res

    def _new_id(self):
        return uuid.uuid4().hex

    def _init_available_images(self):
        """Provides the available images"""
        return [
            _Image(
                id="sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",  # noqa
                name='simphonyproject/simphony-mayavi',
                labels={
                    SIMPHONY_NS.description: 'Ubuntu machine with mayavi preinstalled',  # noqa
                    SIMPHONY_NS.ui_name: 'Mayavi 4.4.4',
                    SIMPHONY_NS.type: 'vncapp',
                    SIMPHONY_NS_ENV['x11-width']: '',
                    SIMPHONY_NS_ENV['x11-height']: '',
                    SIMPHONY_NS_ENV['x11-depth']: '',
                },
                exposed_ports={
                    "8888/tcp": {}
                }
            ),
            _Image(
                id="sha256:86acc3c585a1bb1f3be294c2a02fc69a145e5e76d580a5c7c120ff1ecd1a86ab",  # noqa
                name='simphonyproject/ubuntu-image',
                labels={
                    SIMPHONY_NS.description: 'A vanilla Ubuntu installation',  # noqa
                },
                exposed_ports={
                    "8888/tcp": {}
                }
            )]
