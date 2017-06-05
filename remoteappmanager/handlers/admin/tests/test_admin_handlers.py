from tornado.testing import LogTrapTestCase
from remoteappmanager.tests import utils
from remoteappmanager.tests.mocking import dummy


class TestBaseAccess(utils.AsyncHTTPTestCase, LogTrapTestCase):
    #: which url to poke
    url = "/user/johndoe"

    # which string we expect in the body to say it's ok
    body_string = "adminoptions"

    def get_app(self):
        app = dummy.create_admin_application()
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_access(self):
        res = self.fetch(self.url,
                         headers={
                             "Cookie": "jupyter-hub-token-johndoe=foo"
                         }
                         )

        self.assertEqual(res.code, 200)
        self.assertIn(self.body_string, str(res.body))

    def test_failed_auth(self):
        self._app.hub.verify_token.return_value = {}
        res = self.fetch(self.url,
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         }
                         )

        self.assertGreaterEqual(res.code, 400)
        self.assertIn(self._app.file_config.login_url, res.effective_url)
        self.assertNotIn(self.body_string, str(res.body))


class TestApplicationsHandler(TestBaseAccess):
    url = "/user/johndoe/#/applications/"
    body_string = '<section class="content">'


class TestUsersHandler(TestBaseAccess):
    url = "/user/johndoe/#/users/"
    body_string = '<section class="content">'


class TestContainersHandler(TestBaseAccess):
    url = "/user/johndoe/#/containers/"
    body_string = '<section class="content">'


class TestAccountingHandler(TestBaseAccess):
    url = "/user/johndoe/#/users/0/accounting/"
    body_string = '<section class="content">'

    def test_unknown_id(self):
        self._app.db.unexistent_user_id = 123422
        res = self.fetch("/user/johndoe/users/123422/accounting/",
                         headers={
                             "Cookie": "jupyter-hub-token-johndoe=foo"
                         })

        self.assertEqual(res.code, 404)
