from remoteappmanager.handlers.base_handler import BaseHandler
from remoteappmanager.rest import exceptions
from remoteappmanager.rest.http import httpstatus
from remoteappmanager.rest.http.payloaded_http_error import PayloadedHTTPError
from remoteappmanager.rest.registry import registry
from remoteappmanager.utils import url_path_join, with_end_slash
from tornado import gen, web, escape


class RESTBaseHandler(BaseHandler):
    @property
    def registry(self):
        """Returns the global class vs Resource registry"""
        return registry

    def get_resource_handler_or_404(self, collection_name):
        """Given a collection name, inquires the registry
        for its associated Resource class. If not found
        raises HTTPError(NOT_FOUND)"""

        try:
            resource_class = self.registry[collection_name]
            return resource_class(
                application=self.application,
                current_user=self.current_user)
        except KeyError:
            raise web.HTTPError(httpstatus.NOT_FOUND)

    def write_error(self, status_code, **kwargs):
        """Provides appropriate payload to the response in case of error.
        """
        exc_info = kwargs.get("exc_info")

        if exc_info is None:
            self.clear_header('Content-Type')
            self.finish()

        exc = exc_info[1]

        if isinstance(exc, PayloadedHTTPError) and exc.payload is not None:
            self.set_header('Content-Type', exc.content_type)
            self.finish(exc.payload)
        else:
            # For non-payloaded http errors or any other exception
            # we don't want to return anything as payload.
            # The error code is enough.
            self.clear_header('Content-Type')
            self.finish()

    def rest_to_http_exception(self, rest_exc):
        """Converts a REST exception into the appropriate HTTP one."""

        representation = rest_exc.representation()
        payload = None
        content_type = None

        if representation is not None:
            payload = escape.json_encode(representation)
            content_type = "application/json"

        return PayloadedHTTPError(
            status_code=rest_exc.http_code,
            payload=payload,
            content_type=content_type
        )


class RESTCollectionHandler(RESTBaseHandler):
    """Handler for URLs addressing a collection.
    """
    @web.authenticated
    @gen.coroutine
    def get(self, collection_name):
        """Returns the collection of available items"""
        res_handler = self.get_resource_handler_or_404(collection_name)

        try:
            items = yield res_handler.items()
        except exceptions.RESTException as e:
            raise self.rest_to_http_exception(e)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)
        except Exception:
            self.log.exception(
                "Internal error during get operation on {}".format(
                    collection_name,
                ))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        self.set_status(httpstatus.OK)
        # Need to convert into a dict for security issue tornado/1009
        self.write({"items": list(items)})
        self.flush()

    @web.authenticated
    @gen.coroutine
    def post(self, collection_name):
        """Creates a new resource in the collection."""
        res_handler = self.get_resource_handler_or_404(collection_name)

        try:
            data = escape.json_decode(self.request.body)
        except ValueError:
            raise web.HTTPError(httpstatus.BAD_REQUEST)

        try:
            resource_id = yield res_handler.create(data)
        except exceptions.RESTException as e:
            raise self.rest_to_http_exception(e)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)
        except Exception:
            self.log.exception(
                "Internal error during post operation on {}".format(
                    collection_name,
                ))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        if resource_id is None:
            self.log.error(
                "create method for {} returned None".format(collection_name))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        location = with_end_slash(
            url_path_join(self.request.full_url(), resource_id))

        self.set_status(httpstatus.CREATED)
        self.set_header("Location", location)
        self.clear_header('Content-Type')
        self.flush()


class RESTResourceHandler(RESTBaseHandler):
    """Handler for URLs addressing a resource.
    """
    SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE")

    @web.authenticated
    @gen.coroutine
    def get(self, collection_name, identifier):
        """Retrieves the resource representation."""
        res_handler = self.get_resource_handler_or_404(collection_name)

        try:
            representation = yield res_handler.retrieve(identifier)
        except exceptions.RESTException as e:
            raise self.rest_to_http_exception(e)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)
        except Exception:
            self.log.exception(
                "Internal error during get of {}/{}".format(
                    collection_name,
                    identifier))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        self.set_status(httpstatus.OK)
        self.write(representation)
        self.flush()

    @web.authenticated
    @gen.coroutine
    def post(self, collection_name, identifier):
        """This operation is not possible in REST, and results
        in either Conflict or NotFound, depending on the
        presence of a resource at the given URL"""
        res_handler = self.get_resource_handler_or_404(collection_name)

        try:
            exists = yield res_handler.exists(identifier)
        except exceptions.RESTException as e:
            raise self.rest_to_http_exception(e)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)
        except Exception:
            self.log.exception(
                "Internal error during post of {}/{}".format(
                    collection_name,
                    identifier))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        if exists:
            raise web.HTTPError(httpstatus.CONFLICT)
        else:
            raise web.HTTPError(httpstatus.NOT_FOUND)

    @web.authenticated
    @gen.coroutine
    def put(self, collection_name, identifier):
        """Replaces the resource with a new representation."""
        res_handler = self.get_resource_handler_or_404(collection_name)

        try:
            representation = escape.json_decode(self.request.body)
        except ValueError:
            raise web.HTTPError(httpstatus.UNSUPPORTED_MEDIA_TYPE)

        try:
            yield res_handler.update(identifier, representation)
        except exceptions.RESTException as e:
            raise self.rest_to_http_exception(e)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)
        except Exception:
            self.log.exception(
                "Internal error during put of {}/{}".format(
                    collection_name,
                    identifier))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        self.clear_header('Content-Type')
        self.set_status(httpstatus.NO_CONTENT)

    @web.authenticated
    @gen.coroutine
    def delete(self, collection_name, identifier):
        """Deletes the resource."""
        res_handler = self.get_resource_handler_or_404(collection_name)
        try:
            yield res_handler.delete(identifier)
        except exceptions.RESTException as e:
            raise self.rest_to_http_exception(e)
        except NotImplementedError:
            raise web.HTTPError(httpstatus.METHOD_NOT_ALLOWED)
        except Exception:
            self.log.exception(
                "Internal error during delete of {}/{}".format(
                    collection_name,
                    identifier))
            raise web.HTTPError(httpstatus.INTERNAL_SERVER_ERROR)

        self.clear_header('Content-Type')
        self.set_status(httpstatus.NO_CONTENT)
