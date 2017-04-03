import contextlib
import sys
import socket
import functools

import tornado.netutil
import tornado.testing
from tornado import gen

from remoteappmanager.command_line_config import CommandLineConfig
from remoteappmanager.file_config import FileConfig
from remoteappmanager.environment_config import EnvironmentConfig
from remoteappmanager.db.orm import Database
from remoteappmanager.tests import fixtures
from remoteappmanager.utils import remove_quotes

# A set of viable start arguments. As they would arrive from outside
arguments = {
    "user": "username",
    "port": 57022,
    "cookie-name": "jupyter-hub-token-username",
    "base-urlpath": "\"/user/username/\"",
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
    options = {k.replace("-", "_"): remove_quotes(v)
               for k, v in arguments.items()}

    return CommandLineConfig(**options)


def basic_file_config():
    return FileConfig()


def basic_environment_config():
    config = EnvironmentConfig()
    config.proxy_api_token = "dummy_token"
    config.jpy_api_token = "dummy_token"

    return config


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
            if isinstance(side_effect, Exception):
                raise side_effect
            else:
                side_effect(*args, **kwargs)
        return coro.return_value

    coro.called = False
    coro.return_value = return_value
    return coro


def assert_containers_equal(test_case, actual, expected):
    test_case.assertEqual(
        set(actual.trait_names()),
        set(expected.trait_names()))

    for name in expected.trait_names():
        if getattr(actual, name) != getattr(expected, name):
            message = '{!r} is not identical to the expected {!r}.'
            test_case.fail(message.format(actual, expected))


def probe(f):
    """Wraps a function/method to add a probe we can check after the call.
    Kind of like mock, but preserves the current behavior."""

    @functools.wraps(f)
    def _f(*args, **kwargs):
        _f.called = True
        _f.call_count += 1

        return f(*args, **kwargs)

    _f.called = False
    _f.call_count = 0

    return _f

