from unittest.mock import Mock

from jupyterhub import orm
from remoteappmanager.services.reverse_proxy import ReverseProxy
from tornado import gen, testing

from remoteappmanager.docker.container import Container


class TestReverseProxy(testing.AsyncTestCase):
    @testing.gen_test
    def test_reverse_proxy_operations(self):
        coroutine_out = None

        @gen.coroutine
        def mock_api_request(self, *args, **kwargs):
            nonlocal coroutine_out
            yield gen.sleep(0.1)
            coroutine_out = dict(args=args, kwargs=kwargs)

        reverse_proxy = ReverseProxy("http://fake/api", "token")
        reverse_proxy._reverse_proxy = Mock(spec=orm.Proxy)
        reverse_proxy._reverse_proxy.api_request = mock_api_request

        container = Container(docker_id="12345", base_urlpath="/foo/")
        yield reverse_proxy.add_container(container)

        self.assertEqual(coroutine_out["kwargs"]["method"], "POST")

        yield reverse_proxy.remove_container(container)

        self.assertEqual(coroutine_out["kwargs"]["method"], "DELETE")
