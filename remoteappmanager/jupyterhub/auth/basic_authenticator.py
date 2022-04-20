from tornado import gen

from jupyterhub.auth import Authenticator
from traitlets import Dict

from .simphony_remote_auth_mixin import SimphonyRemoteAuthMixin


class BasicAuthenticator(SimphonyRemoteAuthMixin, Authenticator):
    """ Simple authenticator based on a fixed set of users"""

    #: Dictionary of regular username: password keys allowed
    user_data = Dict().tag(config=True)

    #: Dictionary of admin username: password keys allowed
    admin_data = Dict().tag(config=True)

    @gen.coroutine
    def authenticate(self, handler, data):

        self.log.warning(
            'This is a basic authenticator with a fixed set '
            'of usernames and passwords.')

        username = data['username']

        if username in self.admin_data:
            if data['password'] == self.admin_data[username]:
                return username

        if username in self.user_data:
            if data['password'] == self.user_data[username]:
                return username
