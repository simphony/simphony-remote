from remoteappmanager.file_config import FileConfig

from remoteappmanager.tests import utils
from remoteappmanager.tests.mocking import dummy
from remoteappmanager.tests.temp_mixin import TempMixin


class TestBaseHandler(TempMixin, utils.AsyncHTTPTestCase):
    def get_file_config(self):
        file_config = FileConfig()
        file_config.accounting_class = \
            'remoteappmanager.tests.mocking.dummy.DummyDBAccounting'
        file_config.accounting_kwargs = {}
        return file_config

    def get_app(self):
        file_config = self.get_file_config()

        app = dummy.create_application(file_config=file_config)
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app


class TestBaseHandlerInvalidAccounting(TestBaseHandler):
    def get_file_config(self):
        file_config = super().get_file_config()
        file_config.accounting_class = 'this_should_fail'
        return file_config

    def test_home_internal_error(self):
        res = self.fetch("/user/johndoe/",
                         headers={
                             "Cookie": "jupyter-hub-token-johndoe=foo"
                         }
                         )

        self.assertEqual(res.code, 500)
        self.assertIn('Internal Server Error', str(res.body))
        self.assertIn(" Ref.:", str(res.body))


class TestBaseHandlerDatabaseError(TestBaseHandler):
    def get_file_config(self):
        file_config = super().get_file_config()
        file_config.accounting_class = "remoteappmanager.db.orm.AppAccounting"
        return file_config

    def test_home_internal_error(self):
        res = self.fetch("/user/johndoe/",
                         headers={
                             "Cookie": "jupyter-hub-token-johndoe=foo"
                         }
                         )

        self.assertEqual(res.code, 500)
        self.assertIn('Internal Server Error', str(res.body))
        self.assertIn("The database is not initialised properly. Ref.:",
                      str(res.body))


class TestBaseHandlerGATracking(TestBaseHandler):
    def get_file_config(self):
        file_config = super().get_file_config()
        file_config.ga_tracking_id = "UA-12345-6"
        return file_config

    def test_ga_tracking(self):
        res = self.fetch("/user/johndoe/",
                         headers={
                             "Cookie": "jupyter-hub-token-johndoe=foo"
                         }
                         )

        self.assertEqual(res.code, 200)
        self.assertIn("UA-12345-6", str(res.body))
