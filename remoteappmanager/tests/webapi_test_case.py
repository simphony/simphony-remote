from tornado import escape
from .utils import AsyncHTTPTestCase


class WebAPITestCase(AsyncHTTPTestCase):
    def get(self, url, expect_code=None):

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
        return None
