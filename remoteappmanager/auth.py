from tornado import gen
from jupyterhub.auth import Authenticator


class WorldAuthenticator(Authenticator):
    ''' This authenticator authenticates everyone '''

    @gen.coroutine
    def authenticate(self, handler, data):
        return data['username']
