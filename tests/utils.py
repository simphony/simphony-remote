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
