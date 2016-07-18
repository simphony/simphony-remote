from unittest import mock

from remoteappmanager.services.reverse_proxy import ReverseProxy
from tests import utils


def MockReverseProxy():
    """Constructor. Returns a mock reverse proxy implementation.
    Named as a class for potential future expansion in mock implementation."""

    mock_revproxy = mock.Mock(spec=ReverseProxy)
    mock_revproxy.register = utils.mock_coro_factory("/")
    mock_revproxy.unregister = utils.mock_coro_factory()

    return mock_revproxy
