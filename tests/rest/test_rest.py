from tornado import web, gen, escape
from collections import OrderedDict

from remoteappmanager import rest
from remoteappmanager.rest.resource import Resource
from remoteappmanager.rest import registry, httpstatus, exceptions

from tests.utils import AsyncHTTPTestCase


class Student(Resource):
    collection = OrderedDict()
    id = 0

    @classmethod
    @gen.coroutine
    def create(cls, representation):
        id = str(cls.id)
        cls.collection[id] = representation
        cls.id += 1
        return id

    @classmethod
    @gen.coroutine
    def retrieve(cls, identifier):
        if identifier not in cls.collection:
            raise exceptions.NotFound()

        return cls.collection[identifier]

    @classmethod
    @gen.coroutine
    def update(cls, identifier, representation):
        if identifier not in cls.collection:
            raise exceptions.NotFound()

        cls.collection[identifier] = representation

    @classmethod
    @gen.coroutine
    def delete(cls, identifier):
        if identifier not in cls.collection:
            raise exceptions.NotFound()

        del cls.collection[identifier]

    @classmethod
    @gen.coroutine
    def items(cls):
        return list(cls.collection.keys())


class TestREST(AsyncHTTPTestCase):
    def setUp(self):
        super().setUp()
        Student.collection = OrderedDict()
        Student.id = 0

    def get_app(self):
        handlers = rest.api_handlers('/')
        registry.registry.register(Student)
        return web.Application(handlers=handlers)

    def test_items(self):
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
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "foo": "bar"
            })
        )

        location = res.headers["Location"]

        res = self.fetch(location)
        self.assertEqual(res.code, httpstatus.OK)

        self.assertEqual(escape.json_decode(res.body),
                         {"foo": "bar"}
                         )

        res = self.fetch("/api/v1/students/1/")
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_post_on_resource(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "foo": "bar"
            })
        )

        location = res.headers["Location"]
        res = self.fetch(
            location,
            method="POST",
            body=escape.json_encode({
                "foo": "bar"
            })
        )

        self.assertEqual(res.code, httpstatus.CONFLICT)

    def test_update(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "foo": "bar"
            })
        )

        location = res.headers["Location"]

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
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "foo": "bar"
            })
        )

        location = res.headers["Location"]

        res = self.fetch(location, method="DELETE")
        self.assertEqual(res.code, httpstatus.NO_CONTENT)

        res = self.fetch(location)
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

        res = self.fetch("/api/v1/students/1/", method="DELETE")
        self.assertEqual(res.code, httpstatus.NOT_FOUND)
