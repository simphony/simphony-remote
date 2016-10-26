from unittest import mock

from tornado import escape

from remoteappmanager.db.exceptions import UnsupportedOperation
from tornadowebapi.http import httpstatus

from remoteappmanager.tests.mocking import dummy
from remoteappmanager.tests.utils import AsyncHTTPTestCase


class TestApplication(AsyncHTTPTestCase):
    def get_app(self):
        app = dummy.create_admin_application()
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_delete(self):
        res = self.fetch("/user/username/api/v1/applications/0/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=username"
                         })
        self.assertEqual(res.code, httpstatus.NO_CONTENT)

        res = self.fetch("/user/username/api/v1/applications/12345/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=username"
                         })
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

        res = self.fetch("/user/username/api/v1/applications/foo/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=username"
                         })
        self.assertEqual(res.code, httpstatus.BAD_REQUEST)

    def test_unable_to_delete(self):
        with mock.patch("remoteappmanager.tests.mocking."
                        "dummy.DummyDBAccounting.remove_application"
                        ) as mock_delete_app:
            mock_delete_app.side_effect = UnsupportedOperation()
            res = self.fetch("/user/username/api/v1/applications/1/",
                             method="DELETE",
                             headers={
                                 "Cookie":
                                     "jupyter-hub-token-username=username"
                             })
            self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)

    def test_create(self):
        res = self.fetch("/user/username/api/v1/applications/",
                         method="POST",
                         headers={
                             "Cookie": "jupyter-hub-token-username=username"
                         },
                         body=escape.json_encode({"image_name": "foobar"}))

        self.assertEqual(res.code, httpstatus.CREATED)

        res = self.fetch("/user/username/api/v1/applications/",
                         method="POST",
                         headers={
                             "Cookie": "jupyter-hub-token-username=username"
                         },
                         body=escape.json_encode({"image_name": "foobar"}))

        self.assertEqual(res.code, httpstatus.CONFLICT)

    def test_unable_to_create(self):
        with mock.patch("remoteappmanager.tests.mocking."
                        "dummy.DummyDBAccounting.create_application"
                        ) as mock_create_app:
            mock_create_app.side_effect = UnsupportedOperation()
            res = self.fetch("/user/username/api/v1/applications/",
                             method="POST",
                             headers={
                                 "Cookie":
                                     "jupyter-hub-token-username=username"
                             },
                             body=escape.json_encode({"image_name": "foobar"}))
            self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)

    def test_delete_failed_auth(self):
        self._app.hub.verify_token.return_value = {}

        res = self.fetch("/user/username/api/v1/applications/0/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         })

        self.assertGreaterEqual(res.code, 400)
