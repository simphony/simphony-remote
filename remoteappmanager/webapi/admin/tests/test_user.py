from unittest import mock

from remoteappmanager.db.exceptions import UnsupportedOperation
from remoteappmanager.tests.webapi_test_case import WebAPITestCase
from tornadowebapi.http import httpstatus

from remoteappmanager.tests.mocking import dummy


class TestUser(WebAPITestCase):
    def get_app(self):
        app = dummy.create_admin_application()
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_delete(self):
        self.delete("/user/johndoe/api/v1/users/0/",
                    httpstatus.NO_CONTENT)

        self.delete("/user/johndoe/api/v1/users/12345/",
                    httpstatus.NOT_FOUND)

        self.delete("/user/johndoe/api/v1/users/foo/",
                    httpstatus.NOT_FOUND)

    def test_unable_to_delete(self):
        with mock.patch("remoteappmanager.tests.mocking."
                        "dummy.DummyDBAccounting.remove_user"
                        ) as mock_delete_user:
            mock_delete_user.side_effect = UnsupportedOperation()
            self.delete("/user/johndoe/api/v1/users/1/",
                        httpstatus.INTERNAL_SERVER_ERROR)

    def test_create(self):
        self.post("/user/johndoe/api/v1/users/",
                  {"name": ""},
                  httpstatus.BAD_REQUEST)

        self.post("/user/johndoe/api/v1/users/",
                  {},
                  httpstatus.BAD_REQUEST)

        self.post("/user/johndoe/api/v1/users/",
                  {"name": "foobar"},
                  httpstatus.CREATED)

        self.post("/user/johndoe/api/v1/users/",
                  {"name": "foobar"},
                  httpstatus.CONFLICT)

    def test_unable_to_create(self):
        with mock.patch("remoteappmanager.tests.mocking."
                        "dummy.DummyDBAccounting.create_user"
                        ) as mock_create_user:
            mock_create_user.side_effect = UnsupportedOperation()
            self.post("/user/johndoe/api/v1/users/",
                      {"name": "foobar"},
                      httpstatus.INTERNAL_SERVER_ERROR)

    def test_delete_failed_auth(self):
        self._app.hub.verify_token.return_value = {}

        self.delete("/user/johndoe/api/v1/users/0/",
                    httpstatus.NOT_FOUND)

    def cookie_auth_token(self):
        return "jupyter-hub-token-johndoe=johndoe"
