from unittest import mock

from tornado import testing
from tornado.httpclient import HTTPError

from remoteappmanager.services.hub import Hub


class TestHub(testing.AsyncTestCase):
    def test_initialization(self):
        endpoint_url = "http://example.com/"
        api_key = "whatever"
        hub = Hub(endpoint_url=endpoint_url, api_key=api_key)
        self.assertEqual(hub.endpoint_url, endpoint_url)
        self.assertEqual(hub.api_key, api_key)

    def test_requests(self):
        class Result403:
            status_code = 403
            reason = "403"

        class Result500:
            status_code = 500
            reason = "500"

        class Result200:
            status_code = 200

        endpoint_url = "http://example.com/"
        api_key = "whatever"
        hub = Hub(endpoint_url=endpoint_url, api_key=api_key)

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value = Result403

            with self.assertRaises(HTTPError):
                hub.verify_token("foo", "bar")

            mock_get.return_value = Result500

            with self.assertRaises(HTTPError):
                hub.verify_token("foo", "bar")

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value = Result200

            self.assertTrue(hub.verify_token("foo", "bar"))

            mock_get.assert_called_once_with(
                "http://example.com/authorizations/cookie/foo/bar",
                headers={'Authorization': 'token whatever'})
