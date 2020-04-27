from tornado import escape
from tornado.testing import ExpectLog

from .utils import AsyncHTTPTestCase


class WebAPITestCase(AsyncHTTPTestCase, ExpectLog):
    """Base class for tests accessing the Web API,
    providing basic methods to issue web requests, get results, and compare
    against the expected HTTP code.
    """
    def get(self, url, expect_code=None):
        """Gets a URL.

        Parameters
        ----------
        url: str
            the URL to GET
        expect_code: int
            The expected HTTP code this request should produce.
            If the request produces a different code, the test will fail.

        Returns
        -------
        tuple (code, data), where code is the response HTTP code
        and data is the json decoded representation, or None if the decoding
        fails.
        """

        cookie = self.cookie_auth_token()
        kwargs = {}
        if cookie:
            kwargs["headers"] = {
                "Cookie": cookie
            }
        res = self.fetch(url, **kwargs)

        try:
            data = escape.json_decode(res.body)
        except Exception:
            data = None

        if expect_code:
            self.assertEqual(expect_code, res.code)

        return res.code, data

    def post(self, url, data, expect_code=None):
        """POST to a URL.

        Parameters
        ----------
        url: str
            the URL to POST
        data: dict
            The data to post (after json encoding).
        expect_code: int
            The expected HTTP code this request should produce.
            If the request produces a different code, the test will fail.

        Returns
        -------
        tuple (code, data), where code is the response HTTP code
        and data is the json decoded representation, or None if the decoding
        fails.
        """
        cookie = self.cookie_auth_token()
        kwargs = {}
        if cookie:
            kwargs["headers"] = {
                "Cookie": cookie
            }

        res = self.fetch(
            url,
            method="POST",
            body=escape.json_encode(data),
            **kwargs
        )

        try:
            ret_data = escape.json_decode(res.body)
        except Exception:
            ret_data = None

        if expect_code:
            self.assertEqual(expect_code, res.code)

        return res.code, ret_data

    def delete(self, url, expect_code=None):
        """DELETE a URL.

        Parameters
        ----------
        url: str
            the URL to POST
        expect_code: int
            The expected HTTP code this request should produce.
            If the request produces a different code, the test will fail.

        Returns
        -------
        tuple (code, data), where code is the response HTTP code
        and data is the json decoded representation, or None if
        the decoding fails.
        """
        cookie = self.cookie_auth_token()
        kwargs = {}
        if cookie:
            kwargs["headers"] = {
                "Cookie": cookie
            }

        res = self.fetch(url,
                         method="DELETE",
                         **kwargs
                         )
        try:
            ret_data = escape.json_decode(res.body)
        except Exception:
            ret_data = None

        if expect_code:
            self.assertEqual(expect_code, res.code)

        return res.code, ret_data

    def cookie_auth_token(self):
        """Returns the cookie authorization token.
        Reimplement in the test to pass the appropriate string.
        If None, no cookie will be added to the request."""
        return None
