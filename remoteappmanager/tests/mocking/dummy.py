import uuid
from collections import namedtuple

from remoteappmanager.services.hub import Hub
from remoteappmanager.services.reverse_proxy import ReverseProxy
from remoteappmanager.file_config import FileConfig
from remoteappmanager.application import Application
from remoteappmanager.admin_application import AdminApplication
from remoteappmanager.db import interfaces
from remoteappmanager.db import exceptions
from remoteappmanager.docker.container_manager import ContainerManager

from remoteappmanager.tests.utils import (
    mock_coro_factory,
    basic_command_line_config,
    basic_environment_config)
from remoteappmanager.tests.mocking.virtual.docker_client import (
    VirtualDockerClient)


class DummyDBApplication(interfaces.ABCApplication):
    pass


class DummyDBApplicationPolicy(interfaces.ABCApplicationPolicy):
    pass


class DummyDBAccounting(interfaces.ABCAccounting):
    pass


User = namedtuple('User', ('id', 'name'))


class DummyDB(interfaces.ABCDatabase):
    def __init__(self):
        self.users = {
            0: User(0, "johndoe")
        }

        self.applications = {
            0: DummyDBApplication(
                id=0,
                image='simphonyproject/simphony-mayavi:0.6.0'),
            1: DummyDBApplication(
                id=1,
                image='simphonyproject/ubuntu-image:latest'),
        }

        self.policies = {
            0: DummyDBApplicationPolicy()
        }

        self.accounting = {
            'cbaee2e8ef414f9fb0f1c97416b8aa6c': (
                self.users[0], self.applications[0], self.policies[0]
            ),
            'b7ca425a51bf40acbd305b3f782714b6': (
                self.users[0], self.applications[1], self.policies[0]
            )
        }

    def get_user(self, *, user_name=None, id=None):  # pragma: no cover
        if id is not None:
            return self.users.get(id)

        user = [u for u in self.users.values() if u.name == user_name]
        return user[0] if len(user) else None

    def get_accounting_for_user(self, user):  # pragma: no cover
        return [
                DummyDBAccounting(
                    id=id,
                    user=user,
                    application=application,
                    application_policy=policy)
                for id, (tbl_user, application, policy)
                in self.accounting.items()
                if tbl_user.name == user.name]

    def create_user(self, user_name):  # pragma: no cover
        if user_name in [u.name for u in self.list_users()]:
            raise exceptions.Exists()

        id = len(self.users)
        self.users[id] = User(id, user_name)
        return id

    def remove_user(self, *, user_name=None, id=None):  # pragma: no cover
        if user_name is not None:
            user = [u for u in self.users.values() if u.name == user_name]
            id = user[0] if len(user) else None

        if id is None:
            raise exceptions.NotFound()

        try:
            del self.users[id]
        except KeyError:
            raise exceptions.NotFound()

    def list_users(self):  # pragma: no cover
        return self.users.values()

    def create_application(self, app_name):  # pragma: no cover
        if self._get_application_id_by_name(app_name) is not None:
            raise exceptions.Exists()

        id = len(self.applications)
        self.applications[id] = DummyDBApplication(id, app_name)
        return id

    def remove_application(self, *,
                           app_name=None, id=None):  # pragma: no cover

        if app_name is not None:
            id = self._get_application_id_by_name(app_name)

        if id is None:
            raise exceptions.NotFound()

        try:
            del self.applications[id]
        except KeyError:
            raise exceptions.NotFound()

    def list_applications(self):  # pragma: no cover
        return self.applications.values()

    def grant_access(self, app_name, user_name, app_license,
                     allow_home, allow_view, volume, allow_startup_data):
        app = self._get_application_id_by_name(app_name)
        user = self._get_user_id_by_name(user_name)

        source, target, mode = volume.split(':')
        policy = DummyDBApplicationPolicy(
            app_license, allow_home, allow_view, False, allow_startup_data,
            source, target, mode)

        self.policies[len(self.policies)] = policy
        id = str(uuid.uuid4().hex)
        self.accounting[id] = (user, app, policy)

        return id

    def revoke_access(self, app_name, user_name, app_license,
                      allow_home, allow_view, volume, allow_startup_data):
        pass

    def revoke_access_by_id(self, mapping_id):
        try:
            del self.accounting[mapping_id]
        except KeyError:
            raise exceptions.NotFound()

    def _get_application_id_by_name(self, app_name):
        app = [a for a in self.applications.values()
               if a.image == app_name]
        return app[0] if len(app) else None

    def _get_user_id_by_name(self, user_name):
        user = [u for u in self.users.values()
                if u.name == user_name]
        return user[0] if len(user) else None


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
            "api_token": "dummy_token",
            "endpoint_url": "http://fake.url/"
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
            "api_token": "dummy_token",
            "endpoint_url": "http://fake.url/"
        }

    hub = Hub(**params)

    hub.verify_token = mock_coro_factory({})
    hub.callback_handlers = lambda: []
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
        params = {'docker_config': {}, "realm": "myrealm"}

    manager = ContainerManager(**params)
    manager._docker_client._sync_client = VirtualDockerClient.with_containers()
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
    return _create_application_from_class(Application,
                                          command_line_config,
                                          file_config,
                                          environment_config)


def create_admin_application(command_line_config=None,
                             file_config=None,
                             environment_config=None):
    """Return a dummy Admin Application object

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

    return _create_application_from_class(AdminApplication,
                                          command_line_config,
                                          file_config,
                                          environment_config)


def _create_application_from_class(
        application_class,
        command_line_config=None,
        file_config=None,
        environment_config=None):

    if file_config is None:
        file_config = FileConfig()
        file_config.database_class = \
            'remoteappmanager.tests.mocking.dummy.DummyDB'
        file_config.database_kwargs = {}

    if command_line_config is None:
        command_line_config = basic_command_line_config()

    if environment_config is not None:
        environment_config = basic_environment_config()

    app = application_class(
        command_line_config,
        file_config,
        environment_config)

    app.hub = create_hub()
    app.reverse_proxy = create_reverse_proxy()
    app.container_manager = create_container_manager()

    return app
