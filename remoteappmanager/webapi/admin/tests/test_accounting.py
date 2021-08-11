import urllib.parse
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
        self.delete("/user/johndoe/api/v1/accounting/cbaee2e8ef414f9fb0f1c97416b8aa6c/",  # noqa
                    httpstatus.NO_CONTENT)

        self.delete("/user/johndoe/api/v1/accounting/12345/",
                    httpstatus.NOT_FOUND)

    def test_unable_to_delete(self):
        with mock.patch("remoteappmanager.tests.mocking."
                        "dummy.DummyDB.revoke_access_by_id"
                        ) as mock_delete_user:
            mock_delete_user.side_effect = UnsupportedOperation()
            self.delete("/user/johndoe/api/v1/accounting/cbaee2e8ef414f9fb0f1c97416b8aa6c/",  # noqa
                        httpstatus.INTERNAL_SERVER_ERROR)

    def test_create(self):
        self.post("/user/johndoe/api/v1/accounting/",
                  {"user_id": ""},
                  httpstatus.BAD_REQUEST)

        self.post("/user/johndoe/api/v1/accounting/",
                  {},
                  httpstatus.BAD_REQUEST)

        self.post("/user/johndoe/api/v1/accounting/",
                  {"user_id": "0",
                   "image_name": "image_id1",
                   "app_license": "",
                   "allow_home": True,
                   "volume_source": "/foo",
                   "volume_target": "/bar",
                   "volume_mode": "ro",
                   "allow_startup_data": False,
                   },
                  httpstatus.CREATED)

        # Post in this case is idempotent
        self.post("/user/johndoe/api/v1/accounting/",
                  {"user_id": "0",
                   "image_name": "image_id1",
                   "app_license": "",
                   "allow_home": True,
                   "volume_source": "/foo",
                   "volume_target": "/bar",
                   "volume_mode": "ro",
                   "allow_startup_data": False,
                   },
                  httpstatus.CREATED)

    def test_unable_to_create(self):
        with mock.patch("remoteappmanager.tests.mocking."
                        "dummy.DummyDB.grant_access"
                        ) as mock_grant_access:
            mock_grant_access.side_effect = UnsupportedOperation()
            self.post("/user/johndoe/api/v1/accounting/",
                      {"user_id": "0",
                       "image_name": "image_id1",
                       "app_license": "",
                       "allow_home": True,
                       "volume_source": "/foo",
                       "volume_target": "/bar",
                       "volume_mode": "ro",
                       "allow_startup_data": False,
                       },
                      httpstatus.INTERNAL_SERVER_ERROR)

    def test_unexistent_user_at_create(self):
        self.post("/user/johndoe/api/v1/accounting/",
                  {"user_id": "234",
                   "image_name": "image_id1",
                   "app_license": "",
                   "allow_home": True,
                   "volume_source": "/foo",
                   "volume_target": "/bar",
                   "volume_mode": "ro",
                   "allow_startup_data": False,
                   },
                  httpstatus.BAD_REQUEST)

    def test_absent_volume(self):
        with mock.patch("remoteappmanager.tests.mocking."
                        "dummy.DummyDB.grant_access"
                        ) as mock_grant_access:
            mock_grant_access.return_value = "22"
            self.post("/user/johndoe/api/v1/accounting/",
                      {"user_id": "0",
                       "image_name": "image_id1",
                       "app_license": "",
                       "allow_home": True,
                       "volume_source": "",
                       "volume_target": "",
                       "volume_mode": "",
                       "allow_startup_data": False,
                       },
                      httpstatus.CREATED)
            self.assertEqual(mock_grant_access.call_args[0][5], None)

    def test_items(self):
        self.get("/user/johndoe/api/v1/accounting/", httpstatus.BAD_REQUEST)
        self.get("/user/johndoe/api/v1/accounting/?filter={}",
                 httpstatus.BAD_REQUEST)

        response, data = self.get("/user/johndoe/api/v1/accounting/?filter=" +
                                  urllib.parse.quote("{\"user_id\":\"0\"}"),
                                  httpstatus.OK)
        self.assertEqual(len(data["identifiers"]), 2)

    def test_delete_failed_auth(self):
        self._app.hub.verify_token.return_value = {}

        self.delete("/user/johndoe/api/v1/accounting/cbaee2e8ef414f9fb0f1c97416b8aa6c/",  # noqa
                    httpstatus.NOT_FOUND)

    def cookie_auth_token(self):
        return "jupyter-hub-token-johndoe=johndoe"
