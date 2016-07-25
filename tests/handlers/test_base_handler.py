import os

from tests import utils
from tests.mocking import dummy
from tests.temp_mixin import TempMixin


class TestHomeHandler(TempMixin, utils.AsyncHTTPTestCase):
    def setUp(self):
        self._old_proxy_api_token = os.environ.get("PROXY_API_TOKEN", None)
        os.environ["PROXY_API_TOKEN"] = "dummy_token"

        def cleanup():
            if self._old_proxy_api_token is not None:
                os.environ["PROXY_API_TOKEN"] = self._old_proxy_api_token
            else:
                del os.environ["PROXY_API_TOKEN"]

        self.addCleanup(cleanup)

        super().setUp()

    def get_app(self):
        file_config = dummy.FileConfig()
        file_config.accounting_class = 'this_should_fail'
        file_config.accounting_kwargs = {}

        app = dummy.create_application(file_config=file_config)
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_home(self):
        res = self.fetch("/user/username/",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         }
                         )

        self.assertEqual(res.code, 500)
        self.assertIn('Internal Server Error', str(res.body))
        self.assertIn("Empty module name. Ref.:", str(res.body))
