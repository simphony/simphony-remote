from unittest import mock

from tornado.testing import AsyncHTTPTestCase, ExpectLog

from remoteappmanager.tests.mocking import dummy
from remoteappmanager.tests.temp_mixin import TempMixin


@mock.patch.dict('os.environ', {"JUPYTERHUB_CLIENT_ID": 'client-id'})
@mock.patch('remoteappmanager.handlers.base_handler.BaseHandler._verify_jupyterhub_oauth')  #: noqa:501
class TestUserHomeHandler(TempMixin, AsyncHTTPTestCase):
    def get_app(self):
        app = dummy.create_application()
        app.hub.get_user.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_home(self, mock_verify):
        res = self.fetch("/user/johndoe/",
                         headers={
                             "Cookie": "jupyter-hub-token-johndoe=foo"
                         }
                         )

        self.assertEqual(res.code, 200)
        self.assertIn("applist", str(res.body))

    def test_failed_auth(self, mock_verify):
        self._app.hub.get_user.return_value = {}
        with ExpectLog('tornado.access', ''):
            res = self.fetch("/user/johndoe/",
                             headers={
                                 "Cookie": "jupyter-hub-token-johndoe=foo"
                             }
                             )

        self.assertGreaterEqual(res.code, 400)
        self.assertIn(self._app.file_config.login_url, res.effective_url)
        self.assertNotIn("applist", str(res.body))
