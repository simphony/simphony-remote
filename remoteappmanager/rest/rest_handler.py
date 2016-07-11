from remoteappmanager.rest.registry import registry
from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler


class RESTBaseHandler(BaseHandler):
    _registry = None

    @property
    def registry(self):
        if self.__class__._registry is None:
            self.__class__._registry = registry
        return self._registry


class RESTCollectionHandler(RESTBaseHandler):
    @web.authenticated
    @gen.coroutine
    def get(self, collection_name):
        rest_cls = self.registry[collection_name]

        representation = rest_cls.retrieve()
        self.render(representation,
                    code=200,
                    )

    @web.authenticated
    @gen.coroutine
    def post(self, collection_name):
        rest_cls = self.registry[collection_name]

        resource_id = rest_cls.create()


        self.render(code=201,
                    header={"Location": resource_id}
                    )


class RESTItemHandler(RESTBaseHandler):
    @web.authenticated
    @gen.coroutine
    def get(self, collection_name, identifier):
        rest_cls = self.registry[collection_name]

        pass

    @web.authenticated
    @gen.coroutine
    def post(self):

    @web.authenticated
    @gen.coroutine
    def put(self):
        pass

    @web.authenticated
    @gen.coroutine
    def delete(self):
        pass

