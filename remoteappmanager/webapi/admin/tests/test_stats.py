from tornadowebapi.authenticator import NullAuthenticator
from tornadowebapi.http import httpstatus

from remoteappmanager.tests.webapi_test_case import WebAPITestCase
from remoteappmanager.tests.mocking import dummy


class TestStats(WebAPITestCase):
    def get_app(self):
        app = dummy.create_admin_application()
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_get(self):
        code, data = self.get("/user/johndoe/api/v1/stats/")
        self.assertEqual(code, httpstatus.OK)
        self.assertEqual(data, {
            'num_active_users': 1,
            'num_applications': 2,
            'num_running_containers': 1,
            'num_total_users': 1,
            'realm': 'remoteexec'})

    def cookie_auth_token(self):
        return "jupyter-hub-token-johndoe=johndoe"


class TestContainerNoUser(WebAPITestCase):
    def get_app(self):
        app = dummy.create_admin_application()
        app.registry.authenticator = NullAuthenticator
        return app

    def test_get_no_user(self):
        self.get("/user/johndoe/api/v1/stats/", httpstatus.NOT_FOUND)

    def cookie_auth_token(self):
        return "jupyter-hub-token-johndoe=johndoe"
