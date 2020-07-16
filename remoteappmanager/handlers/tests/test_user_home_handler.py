from tornado.testing import AsyncHTTPTestCase, ExpectLog

from remoteappmanager.tests.mocking import dummy
from remoteappmanager.tests.temp_mixin import TempMixin


class TestUserHomeHandler(TempMixin, AsyncHTTPTestCase):
    def get_app(self):
        app = dummy.create_application()
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_home(self):
        res = self.fetch("/user/johndoe/",
                         headers={
                             "Cookie": "jupyter-hub-token-johndoe=foo"
                         }
                         )

        self.assertEqual(res.code, 200)
        self.assertIn("applist", str(res.body))

    def test_failed_auth(self):
        self._app.hub.verify_token.return_value = {}
        with ExpectLog('tornado.access', ''):
            res = self.fetch("/user/johndoe/",
                             headers={
                                 "Cookie": "jupyter-hub-token-johndoe=foo"
                             }
                             )

        self.assertGreaterEqual(res.code, 400)
        self.assertIn(self._app.file_config.login_url, res.effective_url)
        self.assertNotIn("applist", str(res.body))
