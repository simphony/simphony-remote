from unittest import mock

from remoteappmanager.db.exceptions import UnsupportedOperation
from remoteappmanager.tests.webapi_test_case import WebAPITestCase
from tornadowebapi.http import httpstatus

from remoteappmanager.tests.mocking import dummy


class TestImage(WebAPITestCase):
    def get_app(self):
        app = dummy.create_admin_application()
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_delete(self):
        self.delete("/user/johndoe/api/v1/images/0/",
                    httpstatus.NO_CONTENT)

        self.delete("/user/johndoe/api/v1/images/12345/",
                    httpstatus.NOT_FOUND)

        self.delete("/user/johndoe/api/v1/images/foo/",
                    httpstatus.NOT_FOUND)

    def test_unable_to_delete(self):
        with mock.patch("remoteappmanager.tests.mocking."
                        "dummy.DummyDB.remove_image"
                        ) as mock_delete_image:
            mock_delete_image.side_effect = UnsupportedOperation()
            self.delete("/user/johndoe/api/v1/images/1/",
                        httpstatus.INTERNAL_SERVER_ERROR)

    def test_create(self):
        self.post("/user/johndoe/api/v1/images/",
                  {"name": "foobar"},
                  httpstatus.CREATED)

        self.post("/user/johndoe/api/v1/images/",
                  {"name": "foobar"},
                  httpstatus.CONFLICT)

    def test_unable_to_create(self):
        with mock.patch("remoteappmanager.tests.mocking."
                        "dummy.DummyDB.create_image"
                        ) as mock_create_image:
            mock_create_image.side_effect = UnsupportedOperation()
            self.post("/user/johndoe/api/v1/images/",
                      {"name": "foobar"},
                      httpstatus.INTERNAL_SERVER_ERROR)

    def test_create_invalid_representation(self):
        self.post("/user/johndoe/api/v1/images/",
                  {"name": ""},
                  httpstatus.BAD_REQUEST)

        self.post("/user/johndoe/api/v1/images/",
                  {},
                  httpstatus.BAD_REQUEST)

    def test_delete_failed_auth(self):
        self._app.hub.verify_token.return_value = {}

        self.delete("/user/johndoe/api/v1/images/0/",
                    httpstatus.NOT_FOUND)

    def test_items(self):
        response, data = self.get("/user/johndoe/api/v1/images/",
                                  httpstatus.OK)

        self.assertEqual(data["items"]["0"]["name"],
                         "simphonyproject/simphony-mayavi:0.6.0")

    def cookie_auth_token(self):
        return "jupyter-hub-token-johndoe=johndoe"
