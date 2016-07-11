from tornado import gen

from remoteappmanager.rest.rest_object import RESTObject


class Image(RESTObject):
    @gen.coroutine
    @classmethod
    def list(self):
        return []


class Container(RESTObject):
    @gen.coroutine
    @classmethod
    def list(self):
        return []
