from remoteappmanager.rest.resource import Resource
from tornado import gen


class Image(Resource):
    @classmethod
    @gen.coroutine
    def list(self):
        return []
