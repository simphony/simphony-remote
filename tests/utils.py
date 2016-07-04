import contextlib
import sys
from unittest import mock

import docker
from remoteappmanager.command_line_config import CommandLineConfig
from remoteappmanager.file_config import FileConfig
from remoteappmanager.db.orm import Database
from tests import fixtures


def mock_docker_client():
    """Returns a mock synchronous docker client to return canned
    responses."""
    docker_client = mock.Mock(spec=docker.Client)
    docker_client.inspect_image = mock.Mock(
        return_value={'Created': 1463662803,
                      'Id':
                          'sha256:e54d71dde57576e9d2a4c77ce0c98501c8aa6268de5b2987e4c80e2e157cffe4',  # noqa
                      'Labels': {
                        'eu.simphony-project.docker.description':
                            'Ubuntu machine with mayavi preinstalled'
                      },
                      'ParentId': 'sha256:d2f7240076e135f6aba57185e54ff45cc158781c787897b67994f72fe668ad07',  # noqa
                      'RepoDigests': None,
                      'RepoTags': ['simphony/mayavi-4.4.4:latest'],
                      'Size': 1094833658,
                      'VirtualSize': 1094833658})
    docker_client.inspect_container = mock.Mock(return_value=None)
    docker_client.create_host_config = mock.Mock(return_value={})
    docker_client.create_container = mock.Mock(
        return_value={"Id": "containerid"})
    docker_client.info = mock.Mock(return_value={"ID": "something"})
    docker_client.start = mock.Mock()
    docker_client.port = mock.Mock(
        return_value=[{"HostIp": "127.0.0.1",
                       "HostPort": "666"}]
    )
    docker_client.images = mock.Mock(
        return_value=[
            {'Created': 1463662803,
             'Id': 'sha256:e54d71dde57576e9d2a4c77ce0c98501c8aa6268de5b2987e4c80e2e157cffe4',  # noqa
             'Labels': {
             'eu.simphony-project.docker.description': 'Ubuntu machine with mayavi preinstalled'  # noqa
             },
            'ParentId': 'sha256:d2f7240076e135f6aba57185e54ff45cc158781c787897b67994f72fe668ad07',  # noqa
            'RepoDigests': None,
            'RepoTags': ['simphony/mayavi-4.4.4:latest'],
            'Size': 1094833658,
            'VirtualSize': 1094833658},
            {'Created': 1463662521,
             'Id': 'sha256:ec2d659cbcf0177d6787f2084618cee230aa1207a1d9fff7ed0b561d73abeea7',  # noqa
             'Labels': {'eu.simphony-project.docker.description': 'A vanilla Ubuntu installation'},  # noqa
             'ParentId': 'sha256:8469a0dfd41cdd16402627e0c3e1a256030f36e343c2eb895282bfa16bb54898',  # noqa
             'RepoDigests': None,
             'RepoTags': ['simphony/test-flake8-1.0:latest'],
             'Size': 702751492,
             'VirtualSize': 702751492
             }])
    docker_client.remove_container = mock.Mock()

    return docker_client


def mock_docker_client_with_running_containers():
    """Same as above, but it behaves as if one of the images have two
    containers running for different users."""
    client = mock_docker_client()
    client.containers.return_value = [
        # user
        {'Command': '/sbin/init -D',
         'Created': 1466766499,
         'HostConfig': {'NetworkMode': 'default'},
         'Id': 'someid',
         'Image': 'simphony/mayavi-4.4.4:latest',
         'ImageID': 'imageid',
         'Labels': {
             'eu.simphony-project.docker.user': 'user',
             'eu.simphony-project.docker.mapping_id': 'mapping'
         },
         'Names': ['/remoteexec-image_3Alatest_user'],
         'Ports': [{'IP': '0.0.0.0',
                    'PublicIP': 34567,
                    'PrivatePort': 22,
                    'Type': 'tcp'}],
         'State': 'running',
         'Status': 'Up About an hour'},
    ]

    return client


def mock_docker_client_with_existing_stopped_container():
    """Same as above, but it behaves as if one of the containers is already
    started."""
    client = mock_docker_client()
    client.inspect_container.return_value = {'Args': [],
     'State': {'Paused': False, 'Running': False, 'Error': '', 'Pid': 0,
               'FinishedAt': '2016-06-22T09:15:35.574996772Z',
               'StartedAt': '2016-06-22T09:15:02.196670642Z',
               'Restarting': False, 'Status': 'exited', 'Dead': False,
               'OOMKilled': False, 'ExitCode': 0},
     'LogPath': '/var/lib/docker/containers/9309324cb3f8f02421d702b10759594555aea86345370f027c0fa0f47eb74c39/9309324cb3f8f02421d702b10759594555aea86345370f027c0fa0f47eb74c39-json.log',  # noqa
     'ResolvConfPath': '/var/lib/docker/containers/9309324cb3f8f02421d702b10759594555aea86345370f027c0fa0f47eb74c39/resolv.conf',  # noqa
     'ProcessLabel': '', 'AppArmorProfile': '', 'ExecIDs': None,
     'GraphDriver': {'Name': 'aufs', 'Data': None}, 'MountLabel': '',
     'Name': '/remoteexec-vagrant-simphony_2Fsimphony-remote-docker_3Asimphony-framework-paraview',  # noqa
     'Mounts': [], 'RestartCount': 0,
     'Image': 'sha256:feab698d6f3a93afd5bbb06017201de9a65d1a0119faa62943dbe389f6ea25a0',  # noqa
     'Config': {'Domainname': '', 'WorkingDir': '/tmp', 'AttachStdin': False,
                'StdinOnce': False,
                'Image': 'simphony/simphony-remote-docker:simphony-framework-paraview',  # noqa
                'Hostname': '9309324cb3f8', 'OnBuild': None, 'Tty': False,
                'Labels': {'eu.simphony-project.docker.user': 'vagrant',
                           'eu.simphony-project.docker.description': 'Ubuntu machine with simphony framework preinstalled (with paraview)',  # noqa
                           'eu.simphony-project.docker.ui_name': 'Simphony Framework (w/ Paraview)'},  # noqa
                'AttachStdout': True, 'Volumes': None,
                'Entrypoint': ['/startup.sh'], 'Cmd': None,
                'Env': ['USER=user',
                        'JPY_USER=vagrant',
                        'JPY_BASE_USER_URL=/user/vagrant',
                        'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr'
                        '/bin:/sbin:/bin',
                        'DEBIAN_FRONTEND=noninteractive', 'HOME=/root',
                        'PREFIX=/usr/local',
                        'PYTHONPATH=/usr/local/lib/python2.7/site-packages'],
                'AttachStderr': True, 'ExposedPorts': {'8888/tcp': {}},
                'OpenStdin': False, 'User': ''}, 'Path': '/startup.sh',
     'Driver': 'aufs',
     'Id': '9309324cb3f8f02421d702b10759594555aea86345370f027c0fa0f47eb74c39',
     'Created': '2016-06-22T09:15:01.569475228Z',
     'HostsPath': '/var/lib/docker/containers/9309324cb3f8f02421d702b10759594555aea86345370f027c0fa0f47eb74c39/hosts',  # noqa
     'HostnamePath':
         '/var/lib/docker/containers'
         '/9309324cb3f8f02421d702b10759594555aea86345370f027c0fa0f47eb74c39'
         '/hostname',
     'NetworkSettings': {'EndpointID': '', 'Gateway': '', 'HairpinMode': False,
                         'Ports': None, 'SecondaryIPv6Addresses': None,
                         'SandboxKey': '/var/run/docker/netns/6b4a1da4276f',
                         'Networks': {
                             'bridge': {'IPAMConfig': None, 'EndpointID': '',
                                        'Gateway': '', 'Links': None,
                                        'IPv6Gateway': '',
                                        'GlobalIPv6Address': '',
                                        'MacAddress': '', 'IPPrefixLen': 0,
                                        'Aliases': None, 'IPAddress': '',
                                        'GlobalIPv6PrefixLen': 0,
                                        'NetworkID':
                                            '791e3655381994bb957d40f258f099727cda4ed8473c022d0fd313f68391c118'}},  # noqa
                         'GlobalIPv6Address': '', 'IPPrefixLen': 0,
                         'LinkLocalIPv6PrefixLen': 0, 'MacAddress': '',
                         'Bridge': '', 'LinkLocalIPv6Address': '',
                         'SecondaryIPAddresses': None, 'IPAddress': '',
                         'GlobalIPv6PrefixLen': 0,
                         'SandboxID': '6b4a1da4276f4174fedde241be443a82bba8a840bd0faafb8b490e21af8f5d0f',  # noqa
                         'IPv6Gateway': ''},
     'HostConfig': {'CapDrop': None, 'PublishAllPorts': False, 'PidMode': '',
                    'IpcMode': '', 'CpusetCpus': '', 'Links': None,
                    'PortBindings': {
                        '8888/tcp': [{'HostIp': '', 'HostPort': ''}]},
                    'OomScoreAdj': 0, 'KernelMemory': 0,
                    'BlkioDeviceWriteBps': None, 'CpuShares': 0,
                    'LogConfig': {'Type': 'json-file', 'Config': {}},
                    'DnsOptions': None, 'MemorySwap': 0, 'DiskQuota': 0,
                    'Binds': None, 'Ulimits': None, 'AutoRemove': False,
                    'VolumeDriver': '', 'UsernsMode': '', 'Cgroup': '',
                    'CpusetMems': '', 'ExtraHosts': None,
                    'BlkioDeviceReadIOps': None, 'VolumesFrom': None,
                    'SandboxSize': 0, 'CpuQuota': 0, 'BlkioIOps': 0,
                    'CpuPeriod': 0, 'NetworkMode': 'default',
                    'SecurityOpt': None, 'MemoryReservation': 0,
                    'BlkioWeight': 0, 'ContainerIDFile': '',
                    'BlkioDeviceWriteIOps': None, 'Privileged': False,
                    'GroupAdd': None, 'BlkioDeviceReadBps': None,
                    'DnsSearch': None, 'OomKillDisable': False,
                    'CgroupParent': '', 'BlkioWeightDevice': None, 'Dns': None,
                    'Isolation': '',
                    'RestartPolicy': {'Name': '', 'MaximumRetryCount': 0},
                    'Devices': None, 'MemorySwappiness': -1,
                    'ShmSize': 67108864, 'StorageOpt': None,
                    'ConsoleSize': [0, 0], 'PidsLimit': 0, 'CpuPercent': 0,
                    'BlkioBps': 0, 'UTSMode': '', 'ReadonlyRootfs': False,
                    'Memory': 0, 'CpuCount': 0, 'CapAdd': None}}
    return client


# A set of viable start arguments
arguments = {
    "user": "username",
    "port": 57022,
    "cookie-name": "jupyter-hub-token-username",
    "base-url": "/user/username/",
    "hub-host": "",
    "hub-prefix": "/hub/",
    "hub-api-url": "http://172.17.5.167:8081/hub/api",
    "proxy-api-url": "http://192.168.100.99/proxy/api",
    "ip": "127.0.0.1",
    "config-file": fixtures.get("remoteappmanager_config.py")
}


def init_sqlite_db(path):
    """Initializes the sqlite database at a given path.
    """
    db = Database("sqlite:///"+path)
    db.reset()


def basic_command_line_config():
    """Returns a basic application config for testing purposes.
    The database is in memory.
    """
    options = {k.replace("-", "_"): v for k, v in arguments.items()}

    return CommandLineConfig(**options)


def basic_file_config():
    options = {
        "db_url": "sqlite://"
    }
    return FileConfig(**options)


@contextlib.contextmanager
def invocation_argv():
    """Replaces and restores the argv arguments"""
    saved_argv = sys.argv[:]
    new_args = ["--{}={}".format(key, value)
                for key, value in arguments.items()]
    sys.argv[:] = [sys.argv[0]] + new_args

    yield

    sys.argv[:] = saved_argv


def assert_containers_equal(test_case, actual, expected):
    if (expected.docker_id != actual.docker_id or
            expected.name != actual.name or
            expected.image_name != actual.image_name or
            expected.image_id != actual.image_id or
            expected.ip != actual.ip or
            expected.port != actual.port):
        message = '{!r} is not identical to the expected {!r}'
        test_case.fail(message.format(actual, expected))
