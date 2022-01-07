import contextlib
import sys

from tornado import gen

from remoteappmanager.command_line_config import CommandLineConfig
from remoteappmanager.file_config import FileConfig
from remoteappmanager.environment_config import EnvironmentConfig
from remoteappmanager.db.orm import Database
from remoteappmanager.tests import fixtures
from remoteappmanager.utils import remove_quotes

# A set of viable start arguments. As they would arrive from outside
arguments = {
    "user": "johndoe",
    "port": 57022,
    "cookie-name": "jupyter-hub-token-johndoe",
    "base-urlpath": "\"/user/johndoe/\"",
    "proxy-api-url": "http://192.168.100.99/proxy/api",
    "ip": "127.0.0.1",
    "config-file": fixtures.get("remoteappmanager_config.py")
}

env_config = {
    'JUPYTERHUB_API_TOKEN': 'jpy_token',
    'PROXY_API_TOKEN': 'proxy_token',
    'JUPYTERHUB_HOST': '',
    'JUPYTERHUB_BASE_URL': '/hub/',
    'JUPYTERHUB_API_URL': 'http://172.17.5.167:8081/hub/api',
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
    config.proxy_api_token = env_config['PROXY_API_TOKEN']
    config.jpy_api_token = env_config['JUPYTERHUB_API_TOKEN']
    config.hub_host = env_config['JUPYTERHUB_HOST']
    config.hub_prefix = env_config['JUPYTERHUB_BASE_URL']
    config.hub_api_url = env_config['JUPYTERHUB_API_URL']
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
        coro.call_args = (args, kwargs)
        yield gen.sleep(0.1)
        if side_effect:
            if isinstance(side_effect, Exception):
                raise side_effect
            else:
                side_effect(*args, **kwargs)
        return coro.return_value

    coro.called = False
    coro.call_args = ([], {})
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
