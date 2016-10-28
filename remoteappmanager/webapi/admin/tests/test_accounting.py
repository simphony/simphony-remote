from unittest import mock

from remoteappmanager.db.exceptions import UnsupportedOperation
from remoteappmanager.tests.webapi_test_case import WebAPITestCase
from tornadowebapi.http import httpstatus

from remoteappmanager.tests.mocking import dummy


class TestAccounting(WebAPITestCase):
    def get_app(self):
        app = dummy.create_admin_application()
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_delete(self):
        self.delete("/user/username/api/v1/accounting/mapping_id/",
                    httpstatus.NO_CONTENT)

        self.delete("/user/username/api/v1/accounting/12345/",
                    httpstatus.NOT_FOUND)

    def test_unable_to_delete(self):
        with mock.patch("remoteappmanager.tests.mocking."
                        "dummy.DummyDBAccounting.revoke_access_by_id"
                        ) as mock_delete_user:
            mock_delete_user.side_effect = UnsupportedOperation()
            self.delete("/user/username/api/v1/accounting/mapping_id/",
                        httpstatus.INTERNAL_SERVER_ERROR)

    def test_create(self):
        self.post("/user/username/api/v1/accounting/",
                  {"user_name": ""},
                  httpstatus.BAD_REQUEST)

        self.post("/user/username/api/v1/accounting/",
                  {},
                  httpstatus.BAD_REQUEST)

        self.post("/user/username/api/v1/accounting/",
                  {"user_name": "username",
                   "image_name": "image_id1",
                   "allow_home": True,
                   "volume": "/foo:/bar:ro"
                   },
                  httpstatus.CREATED)

        # Post in this case is idempotent
        self.post("/user/username/api/v1/accounting/",
                  {"user_name": "username",
                   "image_name": "image_id1",
                   "allow_home": True,
                   "volume": "/foo:/bar:ro"
                   },
                  httpstatus.CREATED)

    def test_unable_to_create(self):
        with mock.patch("remoteappmanager.tests.mocking."
                        "dummy.DummyDBAccounting.grant_access"
                        ) as mock_grant_access:
            mock_grant_access.side_effect = UnsupportedOperation()
            self.post("/user/username/api/v1/accounting/",
                      {"user_name": "username",
                       "image_name": "image_id1",
                       "allow_home": True,
                       "volume": "/foo:/bar:ro"
                       },
                      httpstatus.INTERNAL_SERVER_ERROR)

    def test_delete_failed_auth(self):
        self._app.hub.verify_token.return_value = {}

        self.delete("/user/username/api/v1/accounting/mapping_id/",
                    httpstatus.NOT_FOUND)

    def cookie_auth_token(self):
        return "jupyter-hub-token-username=username"
