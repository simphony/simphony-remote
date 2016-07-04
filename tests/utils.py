import contextlib
import sys
from unittest import mock

import docker
from remoteappmanager.application_config import ApplicationConfig
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
             'eu.simphony-project.docker.mapping_id': 'mapping',
             'eu.simphony-project.docker.url_id': 'url_id'
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


def containers_dict():
    """Returns the dictionary that is returned by invoking Client.containers()
    Note that this is different from Client.inspect_container(), which follows
    """
    return {
        'Command': '/startup.sh',
        'Created': 1466584191,
        'HostConfig': {'NetworkMode': 'default'},
        'Id': '849ac3a16d88fe410ba8396988c27b0dfad49ce3a05fa835b8f301e728640d0a',
        'Image': 'simphony/app:simphony-framework-mayavi',
        'ImageID':
            'sha256:92016cfc2901fc11a39829033c81a1b8ed530d84fd1111e6caaa66c81b7ec1a8',
        'Labels': {'eu.simphony-project.docker.description': 'Ubuntu machine '
                                                             'with simphony '
                                                             'framework '
                                                             'preinstalled',
                   'eu.simphony-project.docker.icon_128':
                       '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==',
                   'eu.simphony-project.docker.ui_name': 'Simphony Framework ('
                                                         'w/ '
                                                         'mayavi)'},
        'Mounts': [],
        'Names': ['/cocky_pasteur'],
        'NetworkSettings': {'Networks': {'bridge': {'Aliases': None,
                                                    'EndpointID': '',
                                                    'Gateway': '',
                                                    'GlobalIPv6Address': '',
                                                    'GlobalIPv6PrefixLen': 0,
                                                    'IPAMConfig': None,
                                                    'IPAddress': '',
                                                    'IPPrefixLen': 0,
                                                    'IPv6Gateway': '',
                                                    'Links': None,
                                                    'MacAddress': '',
                                                    'NetworkID': ''}}},
        'Ports': [],
        'State': 'exited',
        'Status': 'Exited (0) 12 days ago'}


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


def basic_application_config():
    """Returns a basic application config for testing purposes.
    The database is in memory.
    """
    options = {k.replace("-", "_"): v for k, v in arguments.items()}

    # Go in memory with the db
    options["db_url"] = "sqlite://"

    return ApplicationConfig(**options)


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
    for name in expected.trait_names():
        if getattr(actual, name) != getattr(expected, name):
            message = '{!r} is not identical to the expected {!r}.'
            test_case.fail(message.format(actual, expected))
