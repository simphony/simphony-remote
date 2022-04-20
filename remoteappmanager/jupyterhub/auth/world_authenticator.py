# This authenticator is not tested and is only used for testing purposes
# This is _not_ an authenticator for our application. It is an authenticator
# for jupyterhub.
from tornado import gen

from jupyterhub.auth import Authenticator

from .simphony_remote_auth_mixin import SimphonyRemoteAuthMixin


class WorldAuthenticator(SimphonyRemoteAuthMixin, Authenticator):
    """ This authenticator authenticates everyone """

    @gen.coroutine
    def authenticate(self, handler, data):

        self.log.warning(
            'This authenticator authenticates everyone for testing.')

        return data['username']
