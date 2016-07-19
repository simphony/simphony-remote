import unittest
import urllib.parse
from unittest import mock

from tests import utils
from tornado import web, gen, escape
from collections import OrderedDict

from remoteappmanager import rest
from remoteappmanager.rest.resource import Resource
from remoteappmanager.rest.rest_handler import RESTResourceHandler, \
    RESTCollectionHandler
from remoteappmanager.rest import registry, httpstatus, exceptions

from tests.utils import AsyncHTTPTestCase


def prepare_side_effect(*args, **kwargs):
    user = mock.Mock()
    user.orm_user = mock.Mock()
    args[0].current_user = user


class Student(Resource):

    collection = OrderedDict()
    id = 0

    @gen.coroutine
    def create(self, representation):
        id = str(type(self).id)
        self.collection[id] = representation
        type(self).id += 1
        return id

    @gen.coroutine
    def retrieve(self, identifier):
        if identifier not in self.collection:
            raise exceptions.NotFound()

        return self.collection[identifier]

    @gen.coroutine
    def update(self, identifier, representation):
        if identifier not in self.collection:
            raise exceptions.NotFound()

        self.collection[identifier] = representation

    @gen.coroutine
    def delete(self, identifier):
        if identifier not in self.collection:
            raise exceptions.NotFound

        del self.collection[identifier]

    @gen.coroutine
    def items(self):
        return list(self.collection.keys())


class UnsupportAll(Resource):
    pass


class Unprocessable(Resource):
    @gen.coroutine
    def create(self, representation):
        raise exceptions.BadRequest()

    @gen.coroutine
    def update(self, identifier, representation):
        raise exceptions.BadRequest()


class UnsupportsCollection(Resource):
    @gen.coroutine
    def items(self):
        raise NotImplementedError()


class Broken(Resource):
    @gen.coroutine
    def boom(self, *args):
        raise Exception("Boom!")

    create = boom
    retrieve = boom
    update = boom
    delete = boom
    items = boom


class TestREST(AsyncHTTPTestCase):
    def setUp(self):
        super().setUp()
        Student.collection = OrderedDict()
        Student.id = 0

    def get_app(self):
        handlers = rest.api_handlers('/')
        registry.registry.register(Student)
        registry.registry.register(UnsupportAll)
        registry.registry.register(Unprocessable)
        registry.registry.register(UnsupportsCollection)
        registry.registry.register(Broken)
        app = web.Application(handlers=handlers)
        app.hub = mock.Mock()
        return app

    def test_items(self):
        with mock.patch("remoteappmanager.handlers.base_handler.BaseHandler"
                        ".prepare",
                        new_callable=utils.mock_coro_new_callable(
                               side_effect=prepare_side_effect)):
            res = self.fetch("/api/v1/students/")

            self.assertEqual(res.code, httpstatus.OK)
            self.assertEqual(escape.json_decode(res.body),
                             {"items": []})

            Student.collection[1] = ""
            Student.collection[2] = ""
            Student.collection[3] = ""

            res = self.fetch("/api/v1/students/")
            self.assertEqual(res.code, httpstatus.OK)
            self.assertEqual(escape.json_decode(res.body),
                             {"items": [1, 2, 3]})

    def test_create(self):
        with mock.patch("remoteappmanager.handlers.base_handler.BaseHandler"
                        ".prepare",
                        new_callable=utils.mock_coro_new_callable(
                            side_effect=prepare_side_effect)):
            res = self.fetch(
                "/api/v1/students/",
                method="POST",
                body=escape.json_encode({
                    "foo": "bar"
                })
            )

            self.assertEqual(res.code, httpstatus.CREATED)
            self.assertIn("api/v1/students/0/", res.headers["Location"])

            res = self.fetch(
                "/api/v1/students/",
                method="POST",
                body=escape.json_encode({
                    "foo": "bar"
                })
            )
            self.assertEqual(res.code, httpstatus.CREATED)
            self.assertIn("api/v1/students/1/", res.headers["Location"])

            res = self.fetch("/api/v1/students/")
            self.assertEqual(res.code, httpstatus.OK)
            self.assertEqual(escape.json_decode(res.body),
                             {"items": ['0', '1']})

    def test_retrieve(self):
        with mock.patch("remoteappmanager.handlers.base_handler.BaseHandler"
                        ".prepare",
                        new_callable=utils.mock_coro_new_callable(
                            side_effect=prepare_side_effect)):
            res = self.fetch(
                "/api/v1/students/",
                method="POST",
                body=escape.json_encode({
                    "foo": "bar"
                })
            )

            location = urllib.parse.urlparse(res.headers["Location"]).path

            res = self.fetch(location)
            self.assertEqual(res.code, httpstatus.OK)

            self.assertEqual(escape.json_decode(res.body),
                             {"foo": "bar"}
                             )

            res = self.fetch("/api/v1/students/1/")
            self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_post_on_resource(self):
        with mock.patch("remoteappmanager.handlers.base_handler.BaseHandler"
                        ".prepare",
                        new_callable=utils.mock_coro_new_callable(
                            side_effect=prepare_side_effect)):
            res = self.fetch(
                "/api/v1/students/",
                method="POST",
                body=escape.json_encode({
                    "foo": "bar"
                })
            )

            location = urllib.parse.urlparse(res.headers["Location"]).path
            res = self.fetch(
                location,
                method="POST",
                body=escape.json_encode({
                    "foo": "bar"
                })
            )

            self.assertEqual(res.code, httpstatus.CONFLICT)

    def test_update(self):
        with mock.patch("remoteappmanager.handlers.base_handler.BaseHandler"
                        ".prepare",
                        new_callable=utils.mock_coro_new_callable(
                            side_effect=prepare_side_effect)):
            res = self.fetch(
                "/api/v1/students/",
                method="POST",
                body=escape.json_encode({
                    "foo": "bar"
                })
            )

            location = urllib.parse.urlparse(res.headers["Location"]).path

            res = self.fetch(
                location,
                method="PUT",
                body=escape.json_encode({
                    "foo": "baz"
                })
            )
            self.assertEqual(res.code, httpstatus.NO_CONTENT)

            res = self.fetch(location)
            self.assertEqual(escape.json_decode(res.body),
                             {"foo": "baz"}
                             )

            res = self.fetch(
                "/api/v1/students/1/",
                method="PUT",
                body=escape.json_encode({
                    "foo": "bar"
                })
            )
            self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_delete(self):
        with mock.patch("remoteappmanager.handlers.base_handler.BaseHandler"
                        ".prepare",
                        new_callable=utils.mock_coro_new_callable(
                            side_effect=prepare_side_effect)):
            res = self.fetch(
                "/api/v1/students/",
                method="POST",
                body=escape.json_encode({
                    "foo": "bar"
                })
            )

            # Unfortunately, self.fetch wants a path and never consider
            # the possibility of a fqdn in the url, but according to
            # REST standard and HTTP standard, location should be absolute.
            location = urllib.parse.urlparse(res.headers["Location"]).path

            res = self.fetch(location, method="DELETE")
            self.assertEqual(res.code, httpstatus.NO_CONTENT)

            res = self.fetch(location)
            self.assertEqual(res.code, httpstatus.NOT_FOUND)

            res = self.fetch("/api/v1/students/1/", method="DELETE")
            self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_unexistent_resource_type(self):
        with mock.patch("remoteappmanager.handlers.base_handler.BaseHandler"
                        ".prepare",
                        new_callable=utils.mock_coro_new_callable(
                            side_effect=prepare_side_effect)):
            res = self.fetch(
                "/api/v1/teachers/",
                method="POST",
                body=escape.json_encode({
                    "foo": "bar"
                })
            )

            self.assertEqual(res.code, httpstatus.NOT_FOUND)

            res = self.fetch(
                "/api/v1/teachers/",
                method="GET",
            )

            self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_post_non_json(self):
        with mock.patch("remoteappmanager.handlers.base_handler.BaseHandler"
                        ".prepare",
                        new_callable=utils.mock_coro_new_callable(
                            side_effect=prepare_side_effect)):
            res = self.fetch(
                "/api/v1/students/",
                method="POST",
                body="hello"
            )
            self.assertEqual(res.code, httpstatus.BAD_REQUEST)

    def test_unsupported_methods(self):
        with mock.patch("remoteappmanager.handlers.base_handler.BaseHandler"
                        ".prepare",
                        new_callable=utils.mock_coro_new_callable(
                            side_effect=prepare_side_effect)):
            res = self.fetch(
                "/api/v1/unsupportalls/",
                method="POST",
                body="{}"
            )
            self.assertEqual(res.code, httpstatus.METHOD_NOT_ALLOWED)

            res = self.fetch(
                "/api/v1/unsupportalls/1/",
                method="GET",
            )
            self.assertEqual(res.code, httpstatus.METHOD_NOT_ALLOWED)

            res = self.fetch(
                "/api/v1/unsupportalls/1/",
                method="DELETE",
            )
            self.assertEqual(res.code, httpstatus.METHOD_NOT_ALLOWED)

            res = self.fetch(
                "/api/v1/unsupportalls/1/",
                method="PUT",
                body="{}"
            )
            self.assertEqual(res.code, httpstatus.METHOD_NOT_ALLOWED)

    def test_unprocessable(self):
        with mock.patch("remoteappmanager.handlers.base_handler.BaseHandler"
                        ".prepare",
                        new_callable=utils.mock_coro_new_callable(
                            side_effect=prepare_side_effect)):
            res = self.fetch(
                "/api/v1/unprocessables/",
                method="POST",
                body="{}"
            )
            self.assertEqual(res.code, httpstatus.BAD_REQUEST)

            res = self.fetch(
                "/api/v1/unprocessables/0/",
                method="PUT",
                body="{}"
            )
            self.assertEqual(res.code, httpstatus.BAD_REQUEST)

    def test_broken(self):
        collection_url = "/api/v1/brokens/"
        with mock.patch("remoteappmanager.handlers.base_handler.BaseHandler"
                        ".prepare",
                        new_callable=utils.mock_coro_new_callable(
                            side_effect=prepare_side_effect)):

            for method, body in [("POST", "{}"), ("PUT", "{}"),
                                 ("GET", None), ("DELETE", None)]:
                res = self.fetch(
                    collection_url+"0/", method=method, body=body)
                self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)

            for method, body in [("POST", "{}"), ("GET", None)]:
                res = self.fetch(collection_url, method=method, body=body)
                self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)

    def test_unsupports_collections(self):
        with mock.patch("remoteappmanager.handlers.base_handler.BaseHandler"
                        ".prepare",
                        new_callable=utils.mock_coro_new_callable(
                            side_effect=prepare_side_effect)):
            res = self.fetch(
                "/api/v1/unsupportscollections/",
                method="GET")
            self.assertEqual(res.code, httpstatus.METHOD_NOT_ALLOWED)


class TestRESTFunctions(unittest.TestCase):
    def test_api_handlers(self):
        handlers = rest.api_handlers("/foo")
        self.assertEqual(handlers[0][0], "/foo/api/v1/(.*)/(.*)/")
        self.assertEqual(handlers[0][1], RESTResourceHandler)
        self.assertEqual(handlers[1][0], "/foo/api/v1/(.*)/")
        self.assertEqual(handlers[1][1], RESTCollectionHandler)
