from tornado import web, gen
from tornado.testing import gen_test, ExpectLog, AsyncHTTPTestCase
from tornado.web import HTTPError

from remoteappmanager.services.hub import Hub


class AuthHandler(web.RequestHandler):
    ret_status = 200

    @gen.coroutine
    def get(self, url):
        if self.ret_status != 200:
            raise HTTPError(self.ret_status)

        self.set_status(self.ret_status)
        self.write({"server": "/user/username",
                    "name": "username",
                    "pending": None,
                    "admin": False})
        self.flush()


class TestHub(AsyncHTTPTestCase):
    def get_app(self):
        self.handler = AuthHandler
        handlers = [
            ("/hub/authorizations/cookie/(.*)", self.handler),
        ]
        app = web.Application(handlers)
        return app

    def test_initialization(self):
        endpoint_url = "http://example.com/"
        api_token = "whatever"
        hub = Hub(endpoint_url=endpoint_url, api_token=api_token)
        self.assertEqual(hub.endpoint_url, endpoint_url)
        self.assertEqual(hub.api_token, api_token)

    def test_invalid_init(self):
        log_msg = "Invalid endpoint url to initialise the hub connection."
        with ExpectLog('tornado.application', log_msg):
            with self.assertRaises(ValueError):
                Hub(endpoint_url="", api_token="dummy")

        log_msg = "Invalid API Token to initialise the hub connection."
        with ExpectLog('tornado.application', log_msg):
            with self.assertRaises(ValueError):
                Hub(endpoint_url="http://fake.url/", api_token="")

    @gen_test
    def test_requests(self):
        endpoint_url = self.get_url("/hub")
        api_token = "whatever"
        hub = Hub(endpoint_url=endpoint_url, api_token=api_token)

        self.handler.ret_status = 403
        with ExpectLog('tornado.access', ''):
            self.assertEqual(
                (yield hub.verify_token("foo", "bar")), {})

        self.handler.ret_status = 501
        with ExpectLog('tornado.access', ''):
            self.assertEqual(
                (yield hub.verify_token("foo", "bar")), {})

        self.handler.ret_status = 200
        res = yield hub.verify_token("foo", "bar")
        self.assertNotEqual(res, {})
        self.assertEqual(res["name"], "username")
