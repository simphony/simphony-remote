from unittest.mock import Mock

from jupyterhub import proxy
from remoteappmanager.services.reverse_proxy import ReverseProxy
from tornado import gen
from tornado.testing import gen_test, AsyncTestCase, ExpectLog


class TestReverseProxy(AsyncTestCase):

    @gen_test
    def test_reverse_proxy_operations(self):
        coroutine_out = None

        @gen.coroutine
        def mock_api_request(self, *args, **kwargs):
            nonlocal coroutine_out
            yield gen.sleep(0.1)
            coroutine_out = dict(args=args, kwargs=kwargs)

        reverse_proxy = ReverseProxy(
            endpoint_url="http://fake/api",
            api_token="token")
        reverse_proxy._reverse_proxy = Mock(spec=proxy.Proxy)
        reverse_proxy._reverse_proxy.api_request = mock_api_request

        yield reverse_proxy.register("/hello/from/me/",
                                     "http://localhost:12312/")

        self.assertEqual(coroutine_out["kwargs"]["method"], "POST")

        yield reverse_proxy.unregister("/hello/from/me/")

        self.assertEqual(coroutine_out["kwargs"]["method"], "DELETE")

    def test_incorrect_init(self):
        log_msg = ("invalid proxy API Token to initialise the "
                   "reverse proxy connection.")
        with ExpectLog('tornado.application', log_msg):
            with self.assertRaises(ValueError):
                ReverseProxy(endpoint_url="http://fake/api", api_token="")

        log_msg = ("invalid proxy endpoint url to initialise the "
                   "reverse proxy connection.")
        with ExpectLog('tornado.application', log_msg):
            with self.assertRaises(ValueError):
                ReverseProxy(endpoint_url="", api_token="foo")
