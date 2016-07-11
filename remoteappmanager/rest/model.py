from tornado import gen

from remoteappmanager.rest.rest_object import RESTObject
from remoteappmanager.rest.registry import registry


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


registry.register(Image)
registry.register(Container)
