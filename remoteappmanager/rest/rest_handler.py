from tornado import gen, web, escape
import json

from remoteappmanager.rest.registry import registry
from remoteappmanager.utils import url_path_join
from remoteappmanager.rest import httpstatus
from remoteappmanager.handlers.base_handler import BaseHandler


class RESTBaseHandler(BaseHandler):
    @property
    def registry(self):
        return registry

    def get_rest_class_or_404(self, collection_name):
        try:
            return self.registry[collection_name]
        except KeyError:
            raise web.HTTPError(404)


class RESTCollectionHandler(RESTBaseHandler):
    @web.authenticated
    @gen.coroutine
    def get(self, collection_name):
        rest_cls = self.get_rest_class_or_404(collection_name)

        items = yield rest_cls.list()

        self.set_status(httpstatus.OK)
        # Need to convert into a dict for issue tornado/1009
        self.write({"items": items})
        self.flush()

    @web.authenticated
    @gen.coroutine
    def post(self, collection_name):
        rest_cls = self.get_rest_class_or_404(collection_name)

        data = escape.json_decode(self.request.body)

        try:
            resource_id = yield rest_cls.create(data)
        except Exception as e:
            raise web.HTTPError(httpstatus.NOT_FOUND, reason=str(e))

        location = url_path_join(
            self.request.path,
            resource_id)

        self.set_status(httpstatus.CREATED)
        self.set_header("Location", location)
        self.flush()


class RESTItemHandler(RESTBaseHandler):
    SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE")

    @web.authenticated
    @gen.coroutine
    def get(self, collection_name, identifier):
        rest_cls = self.get_rest_class_or_404(collection_name)

        representation = yield rest_cls.retrieve(identifier)

        self.set_status(httpstatus.OK)
        self.write(representation)
        self.flush()

    @web.authenticated
    @gen.coroutine
    def post(self, collection_name, identifier):
        rest_cls = self.get_rest_class_or_404(collection_name)

        exists = yield rest_cls.exists(identifier)
        if exists:
            raise web.HTTPError(httpstatus.CONFLICT)
        else:
            raise web.HTTPError(httpstatus.NOT_FOUND)

    @web.authenticated
    @gen.coroutine
    def put(self, collection_name, identifier):
        rest_cls = self.get_rest_class_or_404(collection_name)

        representation = escape.json_decode(self.request.body)

        yield rest_cls.update(identifier, representation)

        self.set_status(httpstatus.NO_CONTENT)

    @web.authenticated
    @gen.coroutine
    def delete(self, collection_name, identifier):
        rest_cls = self.get_rest_class_or_404(collection_name)

        yield rest_cls.delete(identifier)

        self.set_status(httpstatus.NO_CONTENT)
