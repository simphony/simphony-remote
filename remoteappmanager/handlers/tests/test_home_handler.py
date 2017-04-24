from remoteappmanager.tests import utils
from remoteappmanager.tests.mocking import dummy
from remoteappmanager.tests.temp_mixin import TempMixin


class TestHomeHandler(TempMixin, utils.AsyncHTTPTestCase):
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
        self.assertIn("ember_container", str(res.body))

    def test_failed_auth(self):
        self._app.hub.verify_token.return_value = {}
        res = self.fetch("/user/johndoe/",
                         headers={
                             "Cookie": "jupyter-hub-token-johndoe=foo"
                         }
                         )

        self.assertGreaterEqual(res.code, 400)
        self.assertIn(self._app.file_config.login_url, res.effective_url)
        self.assertNotIn("ember_container", str(res.body))
