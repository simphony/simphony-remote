from itertools import cycle
import json
import requests
from unittest import mock

import docker


FAKE_IMAGE_IDS = ('image_id1', 'image_id2')

FAKE_IMAGE_NAMES = ('image_name1', 'image_name2')

FAKE_CONTAINER_IDS = ('container_id1', 'container_id2', 'container_id3')

FAKE_CONTAINER_NAMES = ('remoteexec-username-mapping_5Fid',
                        'remoteexec-username-mapping_5Fid_5Fexited',
                        'remoteexec-username-mapping_5Fid_5Fstopped')


def docker_response(status_code=200, content='',
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


def get_fake_image_labels(num=2):
    samples = cycle(
        (
            {'eu.simphony-project.docker.description': 'Ubuntu machine with mayavi preinstalled',  # noqa
             'eu.simphony-project.docker.ui_name': 'Mayavi 4.4.4',
             'eu.simphony-project.docker.type': 'vncapp',
             'eu.simphony-project.docker.env.x11-width': None,
             },
            {'eu.simphony-project.docker.description': 'A vanilla Ubuntu installation'},  # noqa
        )
    )
    return tuple(next(samples) for _ in range(num))


def get_fake_container_ports(num=3):
    samples = cycle(([{'IP': '0.0.0.0',
                       'PublicPort': 666,
                       'PrivatePort': 8888,
                       'Type': 'tcp'}],
                     [{'PrivatePort': 8889,
                       'Type': 'tcp'}],
                     []))
    return tuple(next(samples) for _ in range(num))


def get_fake_container_states(num=3):
    samples = cycle(('running',
                     'exited',
                     {'Paused': False, 'Running': False, 'Error': '', 'Pid': 0,
                      'FinishedAt': '2016-06-22T09:15:35.574996772Z',
                      'StartedAt': '2016-06-22T09:15:02.196670642Z',
                      'Restarting': False, 'Status': 'exited', 'Dead': False,
                      'OOMKilled': False, 'ExitCode': 0}))
    return tuple(next(samples) for _ in range(num))


def get_fake_container_labels(num=3):
    samples = cycle(({'eu.simphony-project.docker.user': 'user_name',
                      'eu.simphony-project.docker.mapping_id': 'mapping_id',
                      'eu.simphony-project.docker.url_id': 'url_id'},
                     {'eu.simphony-project.docker.user': 'user_name'},
                     {}))
    return tuple(next(samples) for _ in range(num))


def mock_containers(container_ids, container_names,
                    container_ports, container_states, container_labels,
                    image_id, image_name, image_labels):

    def containers(**kwargs):
        results = []

        for container_id, container_name, port, state, labels in zip(
                container_ids, container_names, container_ports,
                container_states, container_labels):

            if state != 'running' and not kwargs.get('all', False):
                continue

            all_labels = image_labels.copy()
            all_labels.update(labels)

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
                 'Id': container_id,
                 'Image': image_name,
                 'ImageID': image_id,
                 'Labels': all_labels,
                 'Names': ['/'+container_name],
                 'Ports': port,
                 'State': state})

        return results

    return containers


def mock_inspect_container(container_ids, container_names,
                           container_ports, container_states, container_labels,
                           image_id, image_name, image_labels):

    def inspect_container(container_name_or_id):
        if container_name_or_id not in container_ids+container_names:
            raise docker.errors.NotFound(
                'Container {} not found'.format(container_name_or_id),
                response=docker_response(404))

        try:
            index = container_ids.index(container_name_or_id)
        except ValueError:
            index = container_names.index(container_name_or_id)

        container_id = container_ids[index]
        container_name = container_names[index]
        container_port = container_ports[index]
        container_state = container_states[index]
        labels = container_labels[index]

        all_labels = image_labels.copy()
        all_labels.update(labels)

        network_settings = {}

        if container_port:
            network_settings['Ports'] = {}

            for port_settings in container_port:
                target = '{}/{}'.format(port_settings.get('PrivatePort', ''),
                                        port_settings.get('Type', 'tcp'))
                host_ip = port_settings.get('IP', '')
                host_port = port_settings.get('PublicPort', '')
                network_settings['Ports'][target] = [
                    {'HostIp': str(host_ip),
                     'HostPort': str(host_port)}]

        return {'State': container_state,
                'Name': '/'+container_name,
                'Image': image_id,
                'Config': {
                    'Image': image_name,
                    'Labels': all_labels},
                'Id': container_id,
                'NetworkSettings': network_settings
                }

    return inspect_container


def mock_inspect_image(image_ids, image_names, image_labels):

    def inspect_image(image_name_or_id):
        if image_name_or_id not in image_ids+image_names:
            raise docker.errors.NotFound(
                'No such image: {}'.format(image_name_or_id),
                response=docker_response(404))

        try:
            index = image_ids.index(image_name_or_id)
        except ValueError:
            index = image_names.index(image_name_or_id)

        image_name = image_names[index]
        image_id = image_ids[index]
        labels = image_labels[index]

        return {'Config': {'Cmd': None,
                           'Domainname': '',
                           'Entrypoint': ['/startup.sh'],
                           'ExposedPorts': {'8888/tcp': {}},
                           'Labels': labels},
                'Id': image_id,
                'RepoTags': [image_name]}

    return inspect_image


def mock_images(image_ids, image_names, image_labels):
    def images():
        return [{'Created': '2 days ago',
                 'Id': image_id,
                 'Labels': label,
                 'RepoTags': [image_name]}
                for image_id, image_name, label in zip(image_ids,
                                                       image_names,
                                                       image_labels)]
    return images


def mock_container_port(container_ids, container_names, container_ports):
    def port(container_name_or_id, *args, **kwargs):
        if container_name_or_id not in container_ids+container_names:
            raise docker.errors.NotFound(
                "No such container: {} ".format(container_name_or_id),
                response=docker_response(404))

        try:
            index = container_ids.index(container_name_or_id)
        except ValueError:
            index = container_names.index(container_name_or_id)

        container_port = container_ports[index]

        if container_port:
            host_ip = container_port[0].get('IP', '')
            host_port = container_port[0].get('PublicPort', '')
        else:
            host_ip = host_port = ''

        return [{'HostIp': host_ip, 'HostPort': host_port}]
    return port


def create_docker_client(image_names=FAKE_IMAGE_NAMES,
                         image_ids=FAKE_IMAGE_IDS,
                         image_labels=None,
                         container_names=FAKE_CONTAINER_NAMES,
                         container_ids=FAKE_CONTAINER_IDS,
                         container_ports=None, container_states=None,
                         container_labels=None):
    """Returns a mock synchronous docker client to return canned
    responses.

    Parameters
    ----------
    image_names : tuple
        tuple of image names the docker client should see

    image_ids : tuple
        tuple of image ids associated with image_names

    image_labels : tuple
        tuple of dict containing the labels associated with
        each image

    container_names : tuple
        Names of the containers the docker client should see

    container_ids : tuple
        tuple of container ids associated with the container_names

    container_ports : tuple
        tuple of lists, each list describe the ports available for each
        container

    container_states : tuple
        tuple of str or dict, states of the corresponding container

    container_labels : tuple
        tuple of dict containing the labels associated with each
        container

    Returns
    -------
    docker_client : mock.Mock
        with specification given by docker.Client
    """
    # Default image labels etc may contain mutable, so they are set here
    if image_labels is None:
        image_labels = get_fake_image_labels(len(image_ids))

    if container_ports is None:
        container_ports = get_fake_container_ports(len(container_ids))

    if container_states is None:
        container_states = get_fake_container_states(len(container_ids))

    if container_labels is None:
        container_labels = get_fake_container_labels(len(container_ids))

    # mock the docker client
    docker_client = mock.Mock(spec=docker.Client)
    docker_client.inspect_image = mock_inspect_image(
        image_ids, image_names, image_labels)

    docker_client.inspect_container = mock_inspect_container(
        container_ids, container_names, container_ports, container_states,
        container_labels, image_ids[0], image_names[0], image_labels[0])

    docker_client.containers = mock_containers(
        container_ids, container_names, container_ports, container_states,
        container_labels, image_ids[0], image_names[0], image_labels[0])

    docker_client.info = mock.Mock(return_value={"ID": "something"})
    docker_client.port = mock_container_port(container_ids,
                                             container_names,
                                             container_ports)
    docker_client.images = mock_images(image_ids, image_names, image_labels)

    # These are basic mocked objects
    docker_client.create_host_config = mock.Mock(return_value={})
    docker_client.create_container = mock.Mock(
        return_value={"Id": container_ids[0]})
    docker_client.start = mock.Mock()
    docker_client.stop = mock.Mock()
    docker_client.remove_container = mock.Mock()

    return docker_client
