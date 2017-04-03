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
                    field_names="id name labels")
_Container = namedtuple("Container",
                        field_names="id name image labels ports state")


class VirtualDockerClient(object):
    """A virtual docker client that behaves like the real thing
    but does nothing. It provides the same interface as dockerpy Client.

    When created, it provides a predefined set of available images.
    """
    def __init__(self):
        self._images = []
        self._containers = []

    @classmethod
    def with_containers(cls):
        self = cls()

        self._images = [
            _Image(
                id="image_id1",
                name='image_name1',
                labels={
                    SIMPHONY_NS.description: 'Ubuntu machine with mayavi preinstalled',  # noqa
                    SIMPHONY_NS.ui_name: 'Mayavi 4.4.4',
                    SIMPHONY_NS.type: 'vncapp',
                    SIMPHONY_NS_ENV['x11-width']: '',
                    SIMPHONY_NS_ENV['x11-height']: '',
                    SIMPHONY_NS_ENV['x11-depth']: '',
                }
            ),
            _Image(
                id="image_id2",
                name='image_name2',
                labels={
                    SIMPHONY_NS.description: 'A vanilla Ubuntu installation',  # noqa
                }
            )]

        self._containers = [
            _Container(
                id="container_id1",
                name="myrealm-username-mapping_5Fid",
                image="image_id1",
                labels={
                    SIMPHONY_NS_RUNINFO.user: 'user_name',
                    SIMPHONY_NS_RUNINFO.mapping_id: 'mapping_id',
                    SIMPHONY_NS_RUNINFO.url_id: 'url_id',
                    SIMPHONY_NS_RUNINFO.realm: 'myrealm',
                    SIMPHONY_NS_RUNINFO.urlpath: '/user/username/containers/url_id'  # noqa
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
                id="container_id2",
                name="myrealm-username-mapping_5Fid_5Fexited",
                image="image_id2",
                labels={
                    SIMPHONY_NS_RUNINFO.user: 'user_name'
                },
                ports=[{
                    "PrivatePort": 8889,
                    "Type": "tcp",
                }],
                state="exited",
            ),
            _Container(
                id="container_id3",
                name="remoteexec-username-mapping_5Fid_5Fstopped",
                image="image_id1",
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
                       'ExitCode': 0}
                ,
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
                ports=[],
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

