from tornado.testing import ExpectLog, AsyncHTTPTestCase

from remoteappmanager.tests.mocking import dummy
from remoteappmanager.tests.temp_mixin import TempMixin
from remoteappmanager.tests.utils import mock_coro_factory


class TestRegisterContainerHandler(TempMixin,
                                   AsyncHTTPTestCase,
                                   ExpectLog):
    def get_app(self):
        app = dummy.create_application()
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_absent_url_id(self):
        res = self.fetch("/user/johndoe/containers/99999/",
                         headers={
                             "Cookie": "jupyter-hub-token-johndoe=foo"
                         }
                         )

        self.assertEqual(res.code, 404)

    def test_present_url_id(self):
        res = self.fetch("/user/johndoe/containers/20dcb84cdbea4b1899447246789093d0/",  # noqa
                         headers={
                             "Cookie": "jupyter-hub-token-johndoe=foo"
                         },
                         follow_redirects=False
                         )

        self.assertEqual(res.code, 302)
        self.assertTrue(self._app.reverse_proxy.register.called)

    def test_failed_auth(self):
        self._app.hub.verify_token.return_value = {}
        res = self.fetch("/user/johndoe/containers/url_id",
                         headers={
                             "Cookie": "jupyter-hub-token-johndoe=foo"
                         },
                         follow_redirects=False
                         )

        # It will be sent to the login instead
        self.assertFalse(self._app.reverse_proxy.register.called)
        self.assertEqual(res.code, 302)

    def test_failure_of_reverse_proxy(self):
        self._app.reverse_proxy.register = mock_coro_factory(
            side_effect=Exception("BOOM"))

        res = self.fetch("/user/johndoe/containers/",
                         headers={
                             "Cookie": "jupyter-hub-token-johndoe=foo"
                         },
                         follow_redirects=False
                         )

        self.assertEqual(res.code, 404)
