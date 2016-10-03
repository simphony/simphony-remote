from remoteappmanager.services.hub import Hub
from remoteappmanager.services.reverse_proxy import ReverseProxy
from remoteappmanager.file_config import FileConfig
from remoteappmanager.application import Application
from remoteappmanager.db import interfaces
from remoteappmanager.docker.container_manager import ContainerManager

from remoteappmanager.tests.utils import (
    mock_coro_factory,
    basic_command_line_config,
    basic_environment_config)
from remoteappmanager.tests.mocking.virtual.docker_client import (
    create_docker_client)


class DummyDBApplication(interfaces.ABCApplication):
    pass


class DummyDBApplicationPolicy(interfaces.ABCApplicationPolicy):
    pass


class DummyDBAccounting(interfaces.ABCAccounting):

    def get_user_by_name(self, user_name):
        return user_name

    def get_apps_for_user(self, account):
        return (('mapping_id',
                 DummyDBApplication(image='image_id1'),
                 DummyDBApplicationPolicy()),
                ('id678',
                 DummyDBApplication(image='image_id1'),
                 DummyDBApplicationPolicy()))


def create_reverse_proxy(params=None,
                         register_result='',
                         unregister_result=''):
    """ Return a ReverseProxy with the given parmaters

    Parameters
    ----------
    params: dict
       keyword arguments for initialising ReverseProxy

    register_result : str
       result of ReverseProxy.register

    unregister_result : str
       result of ReverseProxy.unregister

    Returns
    -------
    ReverseProxy : remoteappmanager.services.reverse_proxy.ReverseProxy
    """
    if params is None:
        params = {
            "api_token": "dummy_token"
        }

    revproxy = ReverseProxy(**params)
    revproxy.register = mock_coro_factory(register_result)
    revproxy.unregister = mock_coro_factory(unregister_result)

    return revproxy


def create_hub(params=None):
    """ Return a dummy Hub object

    Parameters
    ----------
    params : dict
        keyword arguments for initialising Hub

    Returns
    -------
    hub : remoteappmanager.services.hub.Hub
    """
    if params is None:
        params = {
            "api_token": "dummy_token"
        }

    hub = Hub(**params)

    hub.verify_token = mock_coro_factory({})
    return hub


def create_container_manager(params=None):
    ''' Return a dummy ContainerManager object

    Parameters
    ----------
    params : dict
        keyword arguments for initialising ContainerManager

    Returns
    -------
    manager : remoteappmanager.docker.container_manager.ContainerManager
    '''
    if params is None:
        params = {'docker_config': {}}

    manager = ContainerManager(**params)
    manager.docker_client._sync_client = create_docker_client()
    return manager


def create_application(command_line_config=None,
                       file_config=None,
                       environment_config=None):
    """Return a dummy Application object

    Parameters
    ----------
    command_line_config : CommandLineConfig
       Command line config for initialising Application

    file_config : FileConfig
       File config for initialising Application

    environment_config: EnvironmentConfig
        Environment configuration for initialising Application

    Returns
    -------
    application : remoteappmanager.application.Application
    """

    if file_config is None:
        file_config = FileConfig()
        file_config.accounting_class = \
            'remoteappmanager.tests.mocking.dummy.DummyDBAccounting'
        file_config.accounting_kwargs = {}

    if command_line_config is None:
        command_line_config = basic_command_line_config()

    if environment_config is not None:
        environment_config = basic_environment_config()

    app = Application(command_line_config,
                      file_config,
                      environment_config)

    app.hub = create_hub()
    app.reverse_proxy = create_reverse_proxy()
    app.container_manager = create_container_manager()

    return app
