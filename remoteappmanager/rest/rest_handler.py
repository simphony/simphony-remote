from tornado import gen, web, escape

from remoteappmanager.rest.registry import registry
from remoteappmanager.utils import url_path_join, with_end_slash
from remoteappmanager.rest import httpstatus, exceptions


class RESTBaseHandler(web.RequestHandler):
    @property
    def registry(self):
        """Returns the global class vs Resource registry"""
        return registry

    def get_rest_class_or_404(self, collection_name):
        """Given a collection name, inquires the registry
        for its associated Resource class. If not found
        raises HTTPError(NOT_FOUND)"""

        try:
            return self.registry[collection_name]
        except KeyError:
            raise web.HTTPError(httpstatus.NOT_FOUND)


class RESTCollectionHandler(RESTBaseHandler):
    """Handler for URLs addressing a collection.
    """

    @gen.coroutine
    def get(self, collection_name):
        """Returns the collection of avilable items"""
        rest_cls = self.get_rest_class_or_404(collection_name)

        try:
            items = yield rest_cls.items()
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)

        self.set_status(httpstatus.OK)
        # Need to convert into a dict for security issue tornado/1009
        self.write({"items": list(items)})
        self.flush()

    @gen.coroutine
    def post(self, collection_name):
        """Creates a new resource in the collection."""
        rest_cls = self.get_rest_class_or_404(collection_name)

        try:
            data = escape.json_decode(self.request.body)
        except ValueError:
            raise web.HTTPError(httpstatus.UNSUPPORTED_MEDIA_TYPE)

        try:
            resource_id = yield rest_cls.create(data)
        except exceptions.UnprocessableRepresentation:
            raise web.HTTPError(httpstatus.UNPROCESSABLE_ENTITY)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)

        location = with_end_slash(
            url_path_join(self.request.path, resource_id))

        self.set_status(httpstatus.CREATED)
        self.set_header("Location", location)
        self.flush()


class RESTItemHandler(RESTBaseHandler):
    """Handler for URLs addressing a resource.
    """
    SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE")

    @gen.coroutine
    def get(self, collection_name, identifier):
        """Retrieves the resource representation."""
        rest_cls = self.get_rest_class_or_404(collection_name)

        try:
            representation = yield rest_cls.retrieve(identifier)
        except exceptions.NotFound:
            raise web.HTTPError(httpstatus.NOT_FOUND)
        except exceptions.UnprocessableRepresentation:
            raise web.HTTPError(httpstatus.UNPROCESSABLE_ENTITY)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)

        self.set_status(httpstatus.OK)
        self.write(representation)
        self.flush()

    @gen.coroutine
    def post(self, collection_name, identifier):
        """This operation is not possible in REST, and results
        in either Conflict or NotFound, depending on the
        presence of a resource at the given URL"""
        rest_cls = self.get_rest_class_or_404(collection_name)

        try:
            exists = yield rest_cls.exists(identifier)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)

        if exists:
            raise web.HTTPError(httpstatus.CONFLICT)
        else:
            raise web.HTTPError(httpstatus.NOT_FOUND)

    @gen.coroutine
    def put(self, collection_name, identifier):
        """Replaces the resource with a new representation."""
        rest_cls = self.get_rest_class_or_404(collection_name)

        try:
            representation = escape.json_decode(self.request.body)
        except ValueError:
            raise web.HTTPError(httpstatus.UNSUPPORTED_MEDIA_TYPE)

        try:
            yield rest_cls.update(identifier, representation)
        except exceptions.NotFound:
            raise web.HTTPError(httpstatus.NOT_FOUND)
        except exceptions.UnprocessableRepresentation:
            raise web.HTTPError(httpstatus.UNPROCESSABLE_ENTITY)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)

        self.set_status(httpstatus.NO_CONTENT)

    @gen.coroutine
    def delete(self, collection_name, identifier):
        """Deletes the resource."""
        rest_cls = self.get_rest_class_or_404(collection_name)

        try:
            yield rest_cls.delete(identifier)
        except exceptions.NotFound:
            raise web.HTTPError(httpstatus.NOT_FOUND)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)

        self.set_status(httpstatus.NO_CONTENT)
