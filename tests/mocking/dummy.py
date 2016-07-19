from remoteappmanager.services.reverse_proxy import ReverseProxy
from remoteappmanager.file_config import FileConfig
from remoteappmanager.application import Application
from remoteappmanager.db import interfaces

from tests.utils import mock_coro_factory, basic_command_line_config


class DummyApplication(interfaces.ABCApplication):
    pass


class DummyApplicationPolicy(interfaces.ABCApplicationPolicy):
    pass


class DummyAccounting(interfaces.ABCAccounting):

    def get_user_by_name(self, user_name):
        return user_name

    def get_apps_for_user(self, account):
        return (('id1', DummyApplication(), DummyApplicationPolicy()),
                ('id2', DummyApplication(), DummyApplicationPolicy()))


def create_application(command_line_config=None, file_config=None):
    if file_config is None:
        file_config = FileConfig()
        file_config.accounting_class = 'tests.mocking.dummy.DummyAccounting'
        file_config.accounting_kwargs = {}

    if command_line_config is None:
        command_line_config = basic_command_line_config()

    return Application(command_line_config, file_config)


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
        params = {}

    revproxy = ReverseProxy(**params)
    revproxy.register = mock_coro_factory(register_result)
    revproxy.unregister = mock_coro_factory(unregister_result)

    return revproxy
