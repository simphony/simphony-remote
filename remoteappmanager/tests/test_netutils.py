from unittest import mock
from tornado import web
from tornado.testing import AsyncHTTPTestCase, gen_test

from remoteappmanager.tests.utils import mock_coro_new_callable
from remoteappmanager.netutils import wait_for_http_server_2xx


class ShortHandler(web.RequestHandler):
    error_count = 10

    def get(self):
        if type(self).error_count:
            type(self).error_count -= 1
            raise web.HTTPError(500)

        self.set_status(200)
        self.write("hello")
        self.finish()


class LongHandler(ShortHandler):
    error_count = 100000


class TestUtils(AsyncHTTPTestCase):
    def get_app(self):

        app = web.Application(handlers=[('/short', ShortHandler),
                                        ('/long', LongHandler)])
        return app

    @gen_test
    def test_basic(self):
        yield wait_for_http_server_2xx(self.get_url("/short"), timeout=2)

        with self.assertRaises(TimeoutError):
            yield wait_for_http_server_2xx(self.get_url("/long"), timeout=2)

    @gen_test
    def test_failures(self):
        with mock.patch("remoteappmanager.netutils.AsyncHTTPClient.fetch",
                        new_callable=mock_coro_new_callable(
                            side_effect=OSError("boo"))), \
                self.assertRaises(TimeoutError):

            yield wait_for_http_server_2xx(self.get_url("/short"), timeout=1)

        with mock.patch("remoteappmanager.netutils.AsyncHTTPClient.fetch",
                        new_callable=mock_coro_new_callable(
                            side_effect=Exception("boo"))), \
                self.assertRaises(TimeoutError):

            yield wait_for_http_server_2xx(self.get_url("/short"), timeout=1)
