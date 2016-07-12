from remoteappmanager.rest.resource import Resource
from tornado import gen


class Container(Resource):
    @classmethod
    @gen.coroutine
    def list(self):
        return []
