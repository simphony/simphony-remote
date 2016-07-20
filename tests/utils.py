import contextlib
import sys
import socket
from unittest import mock

import tornado.netutil
import tornado.testing
from tornado import gen
import docker

from remoteappmanager.command_line_config import CommandLineConfig
from remoteappmanager.file_config import FileConfig
from remoteappmanager.db.orm import Database
from tests import fixtures


def mock_docker_client():
    """Returns a mock synchronous docker client to return canned
    responses."""
    docker_client = mock.Mock(spec=docker.Client)

    # Note that the structure of the returned dictionary is different
    # for `inspect_image` and for `images`
    # The return value is simplified...
    docker_client.inspect_image = mock.Mock(
        return_value= {
            'Author': 'SimPhoNy Team',
            'Comment': '',
            'Config': {'Cmd': None,
                       'Domainname': '',
                       'Entrypoint': ['/startup.sh'],
                       'Env': ['PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                               'DEBIAN_FRONTEND=noninteractive',
                               'HOME=/root'],
                       'ExposedPorts': {'8888/tcp': {}},
                       'Hostname': 'dfc2eabdf236',
                       'Image': 'sha256:912b31a4e4f185b918999540040bb158e208ce0123fde4be07c188b2ab5aa4bb',
                       'Labels': {'eu.simphony-project.docker.description': 'Ubuntu machine with mayavi preinstalled',  # noqa
                                  'eu.simphony-project.docker.ui_name': 'Mayavi 4.4.4'},  # noqa
                       'OnBuild': [],
                       'OpenStdin': False,
                       'StdinOnce': False,
                       'Tty': False,
                       'User': '',
                       'Volumes': None,
                       'WorkingDir': '/root'},
            'Id': 'sha256:e54d71dde57576e9d2a4c77ce0c98501c8aa6268de5b2987e4c80e2e157cffe4',
            'RepoTags': ['simphony/mayavi-4.4.4:latest'],
            'Size': 668483801,
            'VirtualSize': 668483801})
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
                 'eu.simphony-project.docker.description': 'Ubuntu machine with mayavi preinstalled',  # noqa
                 'eu.simphony-project.docker.ui_name': 'Mayavi 4.4.4'  # noqa
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
    client.inspect_container.return_value = {
        'Config': {
                   'Image': 'simphonyproject/simphonic-mayavi',
                   'Labels': {'eu.simphony-project.docker.description': 'Ubuntu '
                                                                        'machine '
                                                                        'with '
                                                                        'simphony '
                                                                        'framework '
                                                                        'preinstalled',
                              'eu.simphony-project.docker.mapping_id': '1c08c87878634e90af43d799e90f61d2',
                              'eu.simphony-project.docker.ui_name': 'Simphony '
                                                                    'Framework '
                                                                    '(w/ mayavi)',
                              'eu.simphony-project.docker.url_id': '55555555555555555555555555555555',
                              'eu.simphony-project.docker.user': 'username'},
                    },
        'Id': '35d88fe321c3d575ec3be64f54b8967ef49c0dc92395bf4c1e511ed3e6ae0c79',
        'Image': 'sha256:f43b749341ee37b56e7bd8d99f09629f311aaec35a8045a39185b5659edef169',
        'Name': '/remoteexec-username-simphonyproject_2Fsimphonic-mayavi_5F1',
        'NetworkSettings': {
                            'Ports': {'8888/tcp': [{'HostIp': '0.0.0.0',
                                                    'HostPort': '32782'}]},
                           },
    }

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
                   'eu.simphony-project.docker.icon_128': '',
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
    "base-urlpath": "/user/username/",
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
    return FileConfig()


@contextlib.contextmanager
def invocation_argv():
    """Replaces and restores the argv arguments"""
    saved_argv = sys.argv[:]
    new_args = ["--{}={}".format(key, value)
                for key, value in arguments.items()]
    sys.argv[:] = [sys.argv[0]] + new_args

    yield

    sys.argv[:] = saved_argv


# Workaround for tornado bug #1573, already fixed in master, but not yet
# available. Remove when upgrading tornado.
def bind_unused_port(reuse_port=False):
    """Binds a server socket to an available port on localhost.

    Returns a tuple (socket, port).
    """
    sock = tornado.netutil.bind_sockets(None,
                                        '127.0.0.1',
                                        family=socket.AF_INET,
                                        reuse_port=reuse_port)[0]
    port = sock.getsockname()[1]
    return sock, port


class AsyncHTTPTestCase(tornado.testing.AsyncHTTPTestCase):
    """Base class workaround for the above condition."""
    def setUp(self):
        self._bind_unused_port_orig = tornado.testing.bind_unused_port
        tornado.testing.bind_unused_port = bind_unused_port

        def cleanup():
            tornado.testing.bind_unused_port = self._bind_unused_port_orig

        self.addCleanup(cleanup)

        super().setUp()


def mock_coro_new_callable(return_value=None, side_effect=None):
    """Creates a patch suitable callable that returns a coroutine
    with appropriate return value and side effect."""

    coro = mock_coro_factory(return_value, side_effect)

    def new_callable():
        return coro

    return new_callable


def mock_coro_factory(return_value=None, side_effect=None):
    """Creates a mock coroutine with a given return value"""
    @gen.coroutine
    def coro(*args, **kwargs):
        coro.called = True
        yield gen.sleep(0.1)
        if side_effect:
            side_effect(*args, **kwargs)
        return coro.return_value

    coro.called = False
    coro.return_value = return_value
    return coro


def assert_containers_equal(test_case, actual, expected):
    for name in expected.trait_names():
        if getattr(actual, name) != getattr(expected, name):
            message = '{!r} is not identical to the expected {!r}.'
            test_case.fail(message.format(actual, expected))
