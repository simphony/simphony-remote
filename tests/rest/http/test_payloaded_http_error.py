import unittest

from remoteappmanager.rest.http.payloaded_http_error import PayloadedHTTPError


class TestPayloadedHTTPError(unittest.TestCase):
    def test_init(self):
        payloaded = PayloadedHTTPError(500, payload=None)
        self.assertEqual(payloaded.payload, None)
        self.assertEqual(payloaded.content_type, None)

        with self.assertRaises(ValueError):
            PayloadedHTTPError(500, payload=123)

        with self.assertRaises(ValueError):
            PayloadedHTTPError(500, content_type="text/plain")

        payloaded = PayloadedHTTPError(500,
                                       payload="hello",
                                       content_type="text/html")

        self.assertEqual(payloaded.payload, "hello")
        self.assertEqual(payloaded.content_type, "text/html")

        payloaded = PayloadedHTTPError(500, payload="hello")
        self.assertEqual(payloaded.content_type, "text/plain")
        self.assertEqual(payloaded.status_code, 500)
