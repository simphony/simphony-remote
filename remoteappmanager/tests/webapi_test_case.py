from tornado import escape
from .utils import AsyncHTTPTestCase


class WebAPITestCase(AsyncHTTPTestCase):
    def get(self, url, expect_code=None):
        res = self.fetch(url,
                         headers={
                             "Cookie": self.cookie_auth_token()
                         })
        try:
            data = escape.json_decode(res.body)
        except:
            data = None

        if expect_code:
            self.assertEqual(expect_code, res.code)

        return res.code, data

    def post(self, url, data, expect_code=None):
        res = self.fetch(
            url,
            method="POST",
            headers={
                "Cookie": self.cookie_auth_token()
            },
            body=escape.json_encode(data)
        )
        try:
            ret_data = escape.json_decode(res.body)
        except:
            ret_data = None

        if expect_code:
            self.assertEqual(expect_code, res.code)

        return res.code, ret_data

    def delete(self, url, expect_code=None):
        res = self.fetch(url,
                         method="DELETE",
                         headers={
                             "Cookie": self.cookie_auth_token()
                         })
        try:
            ret_data = escape.json_decode(res.body)
        except:
            ret_data = None

        if expect_code:
            self.assertEqual(expect_code, res.code)

        return res.code, ret_data

    def cookie_auth_token(self):
        return None
