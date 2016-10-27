from unittest import mock

from remoteappmanager.db.exceptions import UnsupportedOperation
from remoteappmanager.tests.webapi_test_case import WebAPITestCase
from tornadowebapi.http import httpstatus

from remoteappmanager.tests.mocking import dummy


class TestApplication(WebAPITestCase):
    def get_app(self):
        app = dummy.create_admin_application()
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_delete(self):
        self.delete("/user/username/api/v1/applications/0/",
                    httpstatus.NO_CONTENT)

        self.delete("/user/username/api/v1/applications/12345/",
                    httpstatus.NOT_FOUND)

        self.delete("/user/username/api/v1/applications/foo/",
                    httpstatus.BAD_REQUEST)

    def test_unable_to_delete(self):
        with mock.patch("remoteappmanager.tests.mocking."
                        "dummy.DummyDBAccounting.remove_application"
                        ) as mock_delete_app:
            mock_delete_app.side_effect = UnsupportedOperation()
            self.delete("/user/username/api/v1/applications/1/",
                        httpstatus.INTERNAL_SERVER_ERROR)

    def test_create(self):
        self.post("/user/username/api/v1/applications/",
                  {"image_name": "foobar"},
                  httpstatus.CREATED)

        self.post("/user/username/api/v1/applications/",
                  {"image_name": "foobar"},
                  httpstatus.CONFLICT)

    def test_unable_to_create(self):
        with mock.patch("remoteappmanager.tests.mocking."
                        "dummy.DummyDBAccounting.create_application"
                        ) as mock_create_app:
            mock_create_app.side_effect = UnsupportedOperation()
            self.post("/user/username/api/v1/applications/",
                      {"image_name": "foobar"},
                      httpstatus.INTERNAL_SERVER_ERROR)

    def test_delete_failed_auth(self):
        self._app.hub.verify_token.return_value = {}

        self.delete("/user/username/api/v1/applications/0/",
                    httpstatus.BAD_REQUEST)

    def cookie_auth_token(self):
        return "jupyter-hub-token-username=username"
