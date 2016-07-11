from tornado import testing
from tornado import web, gen
from tornado.httpclient import HTTPError

from remoteappmanager.services.hub import Hub


class AuthHandler(web.RequestHandler):
    ret_status = 200

    @gen.coroutine
    def get(self, url):
        if self.ret_status != 200:
            raise HTTPError(self.ret_status)
        return str(self.ret_status)


class TestHub(testing.AsyncHTTPTestCase):
    def get_app(self):
        self.handler = AuthHandler
        handlers = [
            ("/hub/authorizations/cookie/(.*)", self.handler),
        ]
        app = web.Application(handlers)
        return app

    def test_initialization(self):
        endpoint_url = "http://example.com/"
        api_key = "whatever"
        hub = Hub(endpoint_url=endpoint_url, api_key=api_key)
        self.assertEqual(hub.endpoint_url, endpoint_url)
        self.assertEqual(hub.api_key, api_key)

    @testing.gen_test
    def test_requests(self):
        endpoint_url = self.get_url("/hub")
        api_key = "whatever"

        hub = Hub(endpoint_url=endpoint_url, api_key=api_key)

        AuthHandler.ret_status = 200
        result = yield hub.verify_token("foo", "bar")
        self.assertTrue(result)

        AuthHandler.ret_status = 403
        with self.assertRaises(HTTPError):
            yield hub.verify_token("foo", "bar")

        AuthHandler.ret_status = 500
        with self.assertRaises(HTTPError):
            yield hub.verify_token("foo", "bar")
