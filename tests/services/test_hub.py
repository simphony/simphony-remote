import requests
from unittest import mock

from tornado import testing

from remoteappmanager.services.hub import Hub


def get_result_403():
    response = requests.models.Response()
    response.status_code = 403
    response.reason = "403"
    return response


def get_result_500():
    response = requests.models.Response()
    response.status_code = 500
    response.reason = "500"
    return response


def get_result_200():
    response = requests.models.Response()
    response.status_code = 200
    response.reason = "OK"
    response._content = bytes('{"server": "/user/username", '
                              '"name": "username", '
                              '"pending": null, "admin": false}',
                              encoding='u8')
    return response


class TestHub(testing.AsyncTestCase):
    def test_initialization(self):
        endpoint_url = "http://example.com/"
        api_key = "whatever"
        hub = Hub(endpoint_url=endpoint_url, api_key=api_key)
        self.assertEqual(hub.endpoint_url, endpoint_url)
        self.assertEqual(hub.api_key, api_key)

    def test_requests(self):

        endpoint_url = "http://example.com/"
        api_key = "whatever"
        hub = Hub(endpoint_url=endpoint_url, api_key=api_key)

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value = get_result_403()

            self.assertEqual(hub.verify_token("foo", "bar"), {})

            mock_get.return_value = get_result_500()

            self.assertEqual(hub.verify_token("foo", "bar"), {})

        with mock.patch("requests.get") as mock_get:
            mock_get.return_value = get_result_200()

            self.assertTrue(hub.verify_token("foo", "bar"))

            mock_get.assert_called_once_with(
                "http://example.com/authorizations/cookie/foo/bar",
                headers={'Authorization': 'token whatever'})
